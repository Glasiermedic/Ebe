# Ebe Human-Readable Changelog

This is not a replacement for Git history. It explains the architectural evolution in product terms.

## 2026-07-21

### Session: Serialization Boundary, QueryService Migration, and Public Multi-Entity Queries

#### Completed

- separated relationship loading from Memory Stone serialization;
- added immutable connection bundles;
- reduced relationship loading to three batched queries per collection;
- converted the Memory Stone serializer into a database-independent function;
- preserved the established Memory Stone response shape;
- migrated QueryService to `RetrievalService`;
- preserved deterministic retrieval ordering;
- enabled public multi-entity query responses;
- exposed ordered entity provenance;
- labeled multi-entity retrieval as `entity_union`;
- supported mixed entity types and aliases;
- retained strict HTTP 404 behavior for unresolved candidates;
- removed the temporary multi-entity HTTP 501 boundary.

#### Verification

```text
95 tests passing
0 failures
Ruff passing
Compile checks passing
```

#### Next Milestone

Deterministic retrieval-plan generation for exact graph intersections and progressive fallback.

## 2026-07-19
### Session: Multi-Entity Retrieval Foundation
#### Objective

Implement a dedicated retrieval layer capable of retrieving memory stones for one or more resolved entities while preserving existing API behavior.

#### Completed
Added RetrievalRequest
Added RetrievalResult
Added resolve_entities()
Implemented RetrievalService
Added single-entity retrieval
Extended retrieval to support multi-entity union retrieval
Added duplicate elimination using MemoryStone IDs
Added comprehensive retrieval test suite
Expanded entity resolver test suite

#### Current test status:

83 passing tests
0 failures
Major Architectural Decision

During integration we intentionally did not replace graph_recall.py.

Originally the plan was:

QueryService
    ↓
RetrievalService

After reviewing graph_recall.py, we discovered it performs multiple responsibilities:

graph relationship traversal
ordering
serialization
timeline generation
context generation

Replacing it immediately would mix responsibilities inside the new RetrievalService.

Instead we adopted a staged migration.

New Pipeline Vision
Normalizer
      │
Planner
      │
Resolver
      │
Retriever
      │
Serializer
      │
Response Builder

Retrieval returns ORM models.

Serialization converts ORM models into API representations.

The query service orchestrates the pipeline.

#### Engineering Lessons

Retrieval and serialization are independent responsibilities.

Returning ORM models from retrieval allows:

different serializers
ranking
vector search
graph expansion
API evolution

without modifying retrieval logic.

#### Deferred Work

graph_recall.py remains the production path until the serializer layer is introduced.

#### Next Milestone

Create a dedicated serialization layer capable of converting retrieved MemoryStone ORM objects into API response models


### Serialization boundary approved

After inspecting `graph_recall.py`, the team approved a staged migration rather than immediately replacing the production query path.

Approved architecture:

```text
Normalizer
    ↓
Planner
    ↓
Resolver
    ↓
Retriever
    ↓
Serializer
    ↓
Response Builder
```

Key rules:

- retrieval returns `MemoryStone` ORM/domain objects;
- retrieval does not produce JSON;
- serialization does not execute SQL;
- `graph_recall.py` remains temporarily as the production retrieval-and-serialization path;
- QueryService integration follows completion of the serializer boundary.

This decision avoids changing the existing single-entity API response shape before equivalent serialization behavior is verified.


## 2026-07-17

### Added engineering notebook

Created durable documentation for:

- current state;
- roadmap;
- decisions and approval history;
- milestones;
- architecture;
- development workflow;
- testing;
- graph, vector, memory, and query design.

### Recorded current query boundary

Documented that single-entity queries are implemented and multi-entity queries are explicitly rejected with HTTP 501 until retrieval support exists.

### Proposed retrieval-engine boundary

Recorded EBE-005 as proposed, not approved.

---

## Historical development sequence

### Storage phase

Ebe gained:

- Memory Stone persistence;
- people, places, and events;
- relationships;
- extraction and review.

### Associative recall phase

Ebe gained:

- embeddings;
- semantic search;
- importance-aware ranking.

### Knowledge-graph recall phase

Ebe gained:

- person recall;
- place recall;
- event recall;
- person timeline;
- person context.

### Query phase

Ebe gained:

- natural-language query normalization;
- canonical and alias resolution;
- provenance;
- a modular planner;
- an explicit boundary for unfinished multi-entity behavior.

### Current transition

Ebe is transitioning from entity-specific query orchestration to a general retrieval pipeline capable of graph intersections, semantic fallback, temporal constraints, ranking, and grounded synthesis.
