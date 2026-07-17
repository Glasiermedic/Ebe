# Ebe Architecture

**Updated:** 2026-07-17 11:01 America/Los_Angeles

## Architectural Principles

1. **Single responsibility** — normalization, planning, resolution, retrieval, ranking, and response construction remain separable.
2. **Deterministic before generative** — exact graph and structured retrieval should precede model synthesis.
3. **Provenance is part of the result** — Ebe should explain how an entity and memory were found.
4. **No silent fallback** — relaxed retrieval must be distinguishable from an exact match.
5. **Facts remain separate from interpretation** — biblical or narrative enrichment must not become stored factual memory by accident.
6. **Tests define verified behavior** — a roadmap item is not complete until its acceptance criteria are tested.
7. **Inspect before refactoring** — use the repository snapshot and existing abstractions before proposing replacement code.

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
Graph Recall
    ↓
API Response
```

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
Ranking and Evidence Evaluation
    ↓
Response Builder
    ↓
Optional Grounded Synthesis
    ↓
API Response
```

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

Future boundary.

Owns:

- executing graph and vector retrieval strategies;
- deduplicating memories;
- recording strategy and fallback level;
- returning evidence, not prose.

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

### Response builder

Future boundary.

Owns:

- stable public response shape;
- serialization;
- query, entity, and retrieval provenance;
- warnings;
- unresolved phrases;
- fallback disclosure.

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
