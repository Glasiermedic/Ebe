# Ebe Current State

**Updated:** 2026-07-17 11:01 America/Los_Angeles  
**Project owner:** Wesley  
**Technical planning partner:** ChatGPT  
**Repository root:** `~/projects/ebe`  
**API root:** `~/projects/ebe/apps/api`  
**Current build state reported by Wesley:** Green

---

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

```text
POST /query
    ↓
query router
    ↓
answer_query()
    ↓
normalize_query() -7.17.26 completed
    ↓
create_query_plan()
    ↓
single_entity
    ↓
resolve_single_entity()
    ↓
entity-specific graph recall
    ↓
structured API response
```

Current multi-entity behavior:

```text
Tell me about Laura and Robert
```

produces an explicit HTTP 501 response with candidate phrases. This is intentional. Ebe does not pretend to support multi-entity retrieval before that capability exists.

---

## Current Query Modules

```text
apps/api/app/services/query/
├── __init__.py
├── entity_resolver.py
├── models.py
├── normalizer.py
└── planner.py

apps/api/app/services/query_service.py
apps/api/app/services/graph_recall.py
```

Current responsibilities:

| Component | Responsibility |
|---|---|
| `query_service.py` | Orchestrate the request | - complete
| `normalizer.py` | Convert conversational text to a candidate query | - complete
| `planner.py` | Determine current structural intent and candidate phrases | -complete
| `entity_resolver.py` | Resolve canonical names and aliases | - complete
| `graph_recall.py` | Retrieve directly related memory stones | 

---

## Immediate Constraint

`query_service.py` still contains entity-type retrieval branching. That is retrieval behavior, not orchestration.

The proposed next boundary is:

```text
app/services/query/retrieval.py
```

with an internal request model capable of growing to support:

- multiple entities;
- graph intersections;
- semantic fallback;
- time filters;
- ranking;
- confidence;
- provenance.

This remains a proposal until the corresponding decision is approved.

---

## Current Next Decision

**EBE-005 — Establish retrieval boundary and retrieval request model**

Current status:

```text
Proposed
Approved by: Pending
```

Implementation must not begin merely because it appears in the roadmap. Wesley should approve the decision first.

---

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
