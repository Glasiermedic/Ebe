# Ebe Architecture

**Updated:** 2026-07-19 America/Los_Angeles

## Architectural Principles

1. **Single responsibility** — normalization, planning, resolution, retrieval, serialization, ranking, and response construction remain separable.
2. **Deterministic before generative** — exact graph and structured retrieval should precede model synthesis.
3. **Provenance is part of the result** — Ebe should explain how an entity and memory were found.
4. **No silent fallback** — relaxed retrieval must be distinguishable from an exact match.
5. **Domain objects before transport objects** — retrieval returns ORM/domain objects; serialization converts them into transport representations.
6. **Facts remain separate from interpretation** — biblical or narrative enrichment must not become stored factual memory by accident.
7. **Tests define verified behavior** — a roadmap item is not complete until its acceptance criteria are tested.
8. **Inspect before refactoring** — use the repository snapshot and existing abstractions before proposing replacement code.

---

## Current Architecture

```text
Client
  ↓
FastAPI routers
  ↓
Service layer
  ├── memory creation and review
  ├── extraction
  ├── embeddings and semantic search
  ├── graph recall
  └── query orchestration
  ↓
SQLAlchemy
  ↓
PostgreSQL + pgvector
```

## Current Query Architecture

Two paths currently coexist during the staged migration.

### Production API path

```text
HTTP request
    ↓
Router
    ↓
Query Service
    ↓
Normalizer
    ↓
Initial Planner
    ↓
Single Entity Resolver
    ↓
graph_recall.py
    ├── relationship SQL
    ├── ordering
    └── Memory Stone serialization
    ↓
API Response
```

### Implemented retrieval components

```text
Normalized Query
    ↓
Planner
    ↓
resolve_entities()
    ↓
RetrievalRequest
    ↓
RetrievalService
    ↓
RetrievalResult containing MemoryStone ORM objects
```

The retrieval components support zero, one, or multiple resolved entities and multi-entity union retrieval with deduplication. They are not yet the production API path because the serializer boundary must be completed first.

## Target Query Architecture

```text
HTTP request
    ↓
Router
    ↓
Query Orchestrator
    ↓
Normalizer
    ↓
Intent and Candidate Planner
    ↓
Entity Resolver
    ↓
Retrieval Planner
    ↓
Retrieval Engine
    ├── direct graph retrieval
    ├── graph intersections
    ├── temporal filtering
    ├── constrained vector search
    └── progressive fallback
    ↓
Ranker and Evidence Evaluation
    ↓
Serializer
    ↓
Response Builder
    ↓
Optional Grounded Synthesis
    ↓
API Response
```

The serializer converts retrieved domain objects into stable transport representations. The response builder assembles those serialized objects with query provenance, warnings, and retrieval metadata.

---

---

## Boundary Definitions

### Router

Owns:

- request parsing;
- dependency injection;
- public response model;
- HTTP status translation where appropriate.

Does not own:

- entity lookup;
- graph traversal;
- vector search;
- ranking logic.

### Query orchestrator

Owns:

- calling pipeline components in order;
- passing typed results between components;
- coordinating expected failure modes.

Does not own:

- string normalization rules;
- database query details;
- public response serialization rules after a response builder exists.

### Normalizer

Owns:

- whitespace and punctuation normalization;
- supported conversational-prefix removal;
- preservation of original and normalized text.

Does not own database access or intent resolution.

### Planner

Current role:

- distinguish empty, single-candidate, and simple multi-candidate input;
- produce candidate phrases.

Future role:

- identify richer intent;
- construct a retrieval-oriented plan;
- express uncertainty explicitly.

The planner should remain testable without a database.

### Entity resolver

Owns:

- canonical person, place, and event lookup;
- person alias lookup;
- ambiguity handling;
- match provenance.

It must not silently choose among ambiguous identities.

### Retrieval planner

Future boundary.

Owns:

- exact retrieval steps;
- ordered fallback steps;
- required entity combinations;
- time or relationship constraints;
- strategy metadata.

It should not execute SQL.

### Retrieval engine

Implemented foundational boundary; advanced strategies remain future work.

Owns:

- executing graph and vector retrieval strategies;
- returning `MemoryStone` ORM/domain objects;
- supporting single-entity and multi-entity union retrieval;
- deduplicating memories by stable identity;
- preserving deterministic first-seen order;
- recording strategy and fallback metadata as those capabilities are added.

It does not own JSON serialization or public response construction.

### Ranker

Future boundary.

Owns consistent comparison across:

- exact relationship matches;
- number of matched entities;
- semantic relevance;
- importance;
- temporal relevance;
- source confidence;
- user confirmation.

### Serializer

Approved next boundary.

Owns:

- converting ORM/domain objects into transport representations;
- preserving the established Memory Stone response shape;
- relationship-aware Memory Stone serialization;
- serializer reuse across REST, future conversational, and export consumers.

Does not own:

- SQL execution;
- retrieval strategy;
- query orchestration;
- ranking.

### Response builder

Future boundary.

Owns:

- stable public response shape;
- assembly of serialized entities and memories;
- query, entity, and retrieval provenance;
- warnings;
- unresolved phrases;
- fallback disclosure.

It should not execute retrieval SQL or contain domain serialization rules.

### Optional synthesis

Future boundary.

May:

- summarize retrieved evidence;
- create a narrative;
- provide optional biblical context.

Must not:

- invent memories;
- erase uncertainty;
- present interpretation as stored fact;
- operate without retrieved evidence.

---

## Storage Layers

### Relational layer

Stores canonical facts and associations:

- memory stones;
- people;
- aliases;
- places;
- events;
- relationship types;
- review state;
- timestamps;
- importance.

### Vector layer

Supports associative retrieval:

- conceptual similarity;
- related wording;
- recall when exact entity links are absent;
- hybrid fallback.

Vector similarity is not proof that a memory is about a named entity.

### Graph layer

Represents explicit relationships:

```text
Person ↔ Memory Stone
Place  ↔ Memory Stone
Event  ↔ Memory Stone
```

Graph recall answers:

```text
Which stored memories are explicitly connected to this entity?
```

Vector recall answers:

```text
Which stored memories are conceptually similar to this request?
```

These systems complement rather than replace one another.

### Object storage

Future or external asset layer for:

- photographs;
- audio;
- video;
- documents;
- original source artifacts.

Objects should be referenced by stable metadata rather than treated as a user-facing folder hierarchy.

---

## Compatibility Policy

Before changing a model, migration, or public schema, record:

- migration requirement;
- data backfill;
- rollback strategy;
- API compatibility;
- client impact;
- test impact;
- provenance impact.

Near-term retrieval refactors should avoid database changes until multi-entity requirements are proven.
