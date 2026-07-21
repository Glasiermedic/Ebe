# Ebe Current State

**Updated:** 2026-07-21 America/Los_Angeles
**Project owner:** Wesley
**Technical planning partner:** ChatGPT
**Repository root:** `~/projects/ebe`
**API root:** `~/projects/ebe/apps/api`
**Current build state reported by Wesley:** Green

---

## Authoritative Query Update — 2026-07-21

This section supersedes older query-pipeline descriptions below where they conflict.

### Verified build state

```text
95 tests passing
0 failures
Ruff passing
Compile checks passing
```

### Production query pipeline

```text
POST /query
    ↓
QueryService
    ↓
Normalizer
    ↓
Planner
    ↓
Entity Resolver
    ↓
RetrievalRequest
    ↓
RetrievalService
    ↓
MemoryStone ORM/domain objects
    ↓
Batch relationship loader
    ↓
Pure serializer
    ↓
Single- or multi-entity API response
```

### Serialization boundary

The Memory Stone serializer no longer executes SQL. Relationship metadata is loaded separately using three batched queries per Memory Stone collection: people, places, and events.

### QueryService integration

QueryService no longer dispatches through `graph_recall.py`. It delegates retrieval to `RetrievalService`, then passes retrieved Memory Stone objects through the transport and serializer boundary.

### Public multi-entity behavior

`POST /query` now supports ordered multi-entity requests using strict resolution and explicit `entity_union` retrieval semantics.

- every candidate phrase must resolve;
- unresolved candidates return HTTP 404 and identify the failed phrase;
- ambiguous aliases continue to return HTTP 409;
- candidates are never silently dropped;
- duplicate Memory Stones are removed by ID;
- first-seen ordering is preserved;
- single-entity response behavior remains unchanged.

### Next milestone

Generate deterministic retrieval plans for exact graph intersections and progressive fallback.

## Current Product Definition

Ebe is a personal memory and contextual-recall system built around structured memory stones, entities, graph relationships, vector similarity, and future grounded reasoning.

Ebe is not intended to be only:

- a CRUD application;
- a folder system;
- a vector database;
- a chatbot with unrestricted access to raw memories.

The intended system combines:

```text
PostgreSQL facts
+ graph relationships
+ pgvector associative recall
+ importance and time
+ provenance
+ later grounded synthesis
```

---

## Verified Capabilities

### Memory ingestion and review

- Memory Stone CRUD
- structured person, place, and event extraction
- duplicate detection
- semantic review workflow
- user review resolution
- OpenAI structured extraction
- embedding generation and lifecycle
- importance-aware semantic ranking

### Identity and graph model

- people
- places
- events
- aliases
- memory-to-person relationships
- memory-to-place relationships
- memory-to-event relationships
- deterministic graph recall

### Recall

- semantic vector search
- person graph recall
- place graph recall
- event graph recall
- person timeline
- person context
- related people, places, and events

### Retrieval foundation

- immutable `RetrievalRequest` and `RetrievalResult` contracts
- ordered multi-entity resolution through `resolve_entities()`
- single-entity retrieval through `RetrievalService`
- multi-entity union retrieval
- deduplication by Memory Stone ID
- deterministic first-seen ordering
- 95 automated tests passing

### Natural-language query layer

Supported examples:

```text
Laura
Tell me about Laura
Who is Laura?
Who is Sweets?
```

Current query provenance includes:

```text
original query
normalized query
entity type
matched by
matched value
resolved entity
retrieved memories
```

Alias resolution works. Ambiguous aliases should return an explicit conflict rather than selecting an arbitrary person.

---

## Current Query Pipeline

### Production API path

```text
POST /query
    ↓
query router
    ↓
answer_query()
    ↓
normalize_query()
    ↓
create_query_plan()
    ↓
single_entity
    ↓
resolve_single_entity()
    ↓
graph_recall.py
    ↓
serialize_memory_stone()
    ↓
structured API response
```

The public query endpoint still preserves the established single-entity response behavior. Multi-entity input remains rejected by the production path until serializer equivalence and QueryService integration are completed.

### Implemented retrieval path

```text
Normalized query
    ↓
QueryPlan
    ↓
resolve_entities()
    ↓
RetrievalRequest
    ↓
RetrievalService.retrieve()
    ↓
RetrievalResult[MemoryStone]
```

This path supports one or more resolved entities. Multi-entity retrieval currently uses union semantics and removes duplicate Memory Stones by ID while preserving first-seen order.

## Current Query Modules

```text
apps/api/app/services/query/
├── __init__.py
├── entity_resolver.py
├── models.py
├── normalizer.py
├── planner.py
└── retrieval.py

apps/api/app/services/query_service.py
apps/api/app/services/graph_recall.py
apps/api/app/serializers/memory_stones.py
```

Current responsibilities:

| Component | Responsibility | State |
|---|---|---|
| `query_service.py` | Orchestrate the public query request | Production, legacy retrieval path |
| `normalizer.py` | Convert conversational text to a candidate query | Complete |
| `planner.py` | Determine structural intent and candidate phrases | Complete |
| `entity_resolver.py` | Resolve canonical names and aliases | Complete |
| `retrieval.py` | Return related `MemoryStone` ORM objects for zero, one, or multiple entities | Complete foundation |
| `graph_recall.py` | Relationship SQL, ordering, timelines, context, and production serialization | Temporary mixed-responsibility path |
| `serializers/memory_stones.py` | Serialize individual Memory Stones | Existing; batch/pipeline boundary pending |

## Immediate Constraint

The retrieval boundary is implemented, but the public query service cannot safely switch to it yet because `graph_recall.py` currently combines:

- relationship SQL;
- deterministic ordering;
- Memory Stone serialization;
- timeline construction;
- person-context construction.

Directly encoding ORM objects would risk changing the existing API response shape.

The approved next boundary is a dedicated serializer stage:

```text
RetrievalService
    ↓
MemoryStone ORM objects
    ↓
Serializer
    ↓
stable transport objects
```

After serializer equivalence is verified, QueryService can be integrated with RetrievalService and the retrieval responsibilities in `graph_recall.py` can be retired incrementally.

## Current Next Milestone

**Serialization boundary and QueryService migration**

Status:

```text
Approved
Approved by: Wesley
```

Required sequence:

1. add a collection serializer for retrieved Memory Stones;
2. prove output equivalence with existing `graph_recall.py` responses;
3. integrate `RetrievalService` into `query_service.py`;
4. preserve existing single-entity API behavior;
5. replace the multi-entity HTTP 501 only after the integrated response contract is approved;
6. run focused tests and the complete suite.

## Start-of-Session Checklist

From a fresh Ubuntu terminal:

```bash
cd ~/projects/ebe/apps/api

git status
git branch

docker ps

uv run alembic current
uv run alembic heads

uv run ruff check app migrations tests
uv run python -m compileall app migrations tests
uv run pytest -v

cd ~/projects/ebe
./apps/api/scripts/project_snapshot.sh 2>/dev/null ||     ./scripts/project_snapshot.sh

code .
```

If the snapshot script exists only under one of those paths, use that path consistently and update this document.

Development should begin from a green build unless the active task is explicitly to repair the build.
