# Ebe Milestones

**Updated:** 2026-07-17 11:01 America/Los_Angeles

Milestones record stable vertical slices. A milestone may contain several implementation decisions.

---

## Milestone 1 — Application and database foundation

**Status:** Completed

Established:

- FastAPI application;
- PostgreSQL;
- SQLAlchemy;
- migrations;
- test infrastructure;
- core project organization.

Unlocked:

- durable feature development;
- schema evolution;
- repeatable tests.

---

## Milestone 2 — Memory Stone CRUD

**Status:** Completed

Established:

- create and retrieve memory stones;
- structured schemas;
- serialization;
- timestamps;
- importance.

Unlocked:

- persistent memory storage;
- later entity and embedding relationships.

---

## Milestone 3 — People, places, and events

**Status:** Completed

Established:

- entity models;
- entity endpoints;
- Memory Stone association tables;
- relationship types.

Unlocked:

- explicit graph structure;
- deterministic recall.

---

## Milestone 4 — Structured extraction

**Status:** Completed

Established:

- extraction of people, places, and events;
- structured OpenAI output;
- memory-to-entity linking workflow.

Unlocked:

- conversion from unstructured recollection to a structured memory graph.

---

## Milestone 5 — Duplicate and review workflow

**Status:** Completed

Established:

- duplicate detection;
- semantic review;
- user resolution;
- review state.

Unlocked:

- safer memory ingestion;
- reduced accidental duplication;
- human control over uncertain changes.

---

## Milestone 6 — Embedding lifecycle

**Status:** Completed

Established:

- embedding creation;
- refresh lifecycle;
- pgvector storage.

Unlocked:

- associative recall;
- semantic similarity.

---

## Milestone 7 — Semantic search and importance-aware ranking

**Status:** Completed

Established:

- semantic search endpoint;
- normalized score handling;
- importance-aware retrieval score;
- ranking tests.

Unlocked:

- concept-based memory retrieval;
- future graph-vector fusion.

---

## Milestone 8 — Graph recall by person

**Status:** Completed

Established:

```text
GET /people/{person_id}/memories
```

Behavior:

- explicit relationship retrieval;
- importance and time ordering;
- missing-entity handling.

Lessons:

- a generic 404 indicated route registration failure rather than service behavior;
- route registration must be checked through OpenAPI;
- decorators must remain at module scope;
- `typing.Any` is case-sensitive.

Unlocked:

- direct knowledge-graph recall;
- person timelines and context.

---

## Milestone 9 — Graph recall by place and event

**Status:** Completed

Established:

```text
GET /places/{place_id}/memories
GET /events/{event_id}/memories
```

Refinement:

- factored shared graph-recall behavior into a generic internal helper;
- kept entity-specific functions as thin wrappers.

Unlocked:

- deterministic one-hop recall across all primary entity types.

---

## Milestone 10 — Person timeline

**Status:** Completed

Established:

- chronological memory recall for a person;
- timeline-oriented API behavior.

Unlocked:

- temporal context;
- future before/after questions.

---

## Milestone 11 — Person context

**Status:** Completed

Established a structured person context containing:

- person;
- aliases;
- memories;
- related people;
- related places;
- related events.

Unlocked:

- bounded evidence objects;
- future grounded summaries.

---

## Milestone 12 — Natural-language query endpoint

**Status:** Completed

Established:

```text
POST /query
```

Supported forms include:

```text
Laura
Tell me about Laura
Who is Laura?
```

Unlocked:

- one public query interface;
- separation between API and recall implementation.

---

## Milestone 13 — Alias-aware query resolution and provenance

**Status:** Completed

Established:

- canonical-name matching;
- alias matching;
- normalized-query output;
- `matched_by`;
- `matched_value`.

Unlocked:

- explainable identity resolution;
- future fuzzy matching without losing provenance.

---

## Milestone 14 — Modular query package

**Status:** Completed

Established:

```text
normalizer.py
entity_resolver.py
models.py
planner.py
```

Unlocked:

- independent improvement of query stages;
- reduced regression risk;
- multi-entity planning foundation.

---

## Milestone 15 — Explicit multi-entity boundary

**Status:** Completed

Established:

- simple multi-entity candidate parsing;
- explicit 501 response;
- candidate phrase disclosure.

Unlocked:

- honest API behavior;
- a defined next phase rather than silent partial answers.

---

## Milestone 16 — Engineering notebook

**Status:** Approved and created

Established:

- current state;
- roadmap;
- decision log;
- milestones;
- architecture;
- changelog;
- open questions;
- development and design guides.

Unlocked:

- durable continuity across development sessions;
- explicit approval history;
- auditable plan changes.

---

## Next Milestone — Retrieval boundary

**Status:** Proposed

Target:

- typed retrieval request;
- dedicated retrieval service;
- unchanged current API;
- dedicated unit tests.

Decision:

```text
EBE-005
```
