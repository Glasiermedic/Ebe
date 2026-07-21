# Ebe Engineering Roadmap

**Updated:** 2026-07-17 11:01 America/Los_Angeles
**Owner:** Wesley
**Planning partner:** ChatGPT

## Status Vocabulary

```text
Proposed
Approved
In Progress
Blocked
Completed
Rejected
Superseded
```
## Engineering Principles

The Ebe query engine is developed as a deterministic pipeline.

Each stage has a single responsibility.

Stages communicate through immutable request and result models.

Every stage is independently unit tested before integration.

Integration follows after the stage passes its own test suite.

Public API behavior changes require explicit approval.

## A suggestion from ChatGPT remains `Proposed` until Wesley approves it.

---

# Stage A — Completed Foundation

## A1. Memory Stone foundation — Completed

Capabilities:

- Memory Stone CRUD
- people, places, and events
- explicit relationships
- timestamps and importance
- structured schemas and serialization

## A2. Extraction and memory review — Completed

Capabilities:

- structured extraction
- duplicate detection
- semantic review
- user review resolution
- OpenAI-backed extraction path

## A3. Embeddings and semantic recall — Completed

Capabilities:

- embedding generation and lifecycle
- semantic search
- importance-aware ranking
- bounded retrieval scores

## A4. Deterministic graph recall — Completed

Capabilities:

```text
GET /people/{person_id}/memories
GET /places/{place_id}/memories
GET /events/{event_id}/memories
```

Ordering:

1. importance descending;
2. remembered date descending;
3. creation time descending.

## A5. Person timeline and context — Completed

Capabilities:

- chronological person timeline;
- aliases;
- directly related memories;
- related people;
- related places;
- related events.

## A6. Natural-language single-entity query — Completed

Capabilities:

- natural-language normalization;
- canonical entity resolution;
- alias resolution;
- query provenance;
- person, place, and event recall through one public query endpoint.

## A7. Modular query foundation — Completed

Components:

- normalizer;
- planner;
- entity resolver;
- query orchestrator.

Current planner supports:

```text
single_entity
multi_entity
unknown
```

Multi-entity retrieval is intentionally not implemented yet.

## A8. Repository snapshot process — Completed

A repository snapshot script exists to reduce duplicate modules, stale assumptions, and incompatible code suggestions.

---

# Stage B — Retrieval Pipeline

### Stage B Design Principles

The retrieval pipeline follows a single-responsibility architecture.

Each stage owns exactly one concern.

Query
    ↓
Normalize
    ↓
Plan
    ↓
Resolve
    ↓
Retrieve
    ↓
Serialize
    ↓
Response Builder

Retrieval never returns JSON.

Serialization never executes SQL.

The response builder never performs retrieval.

## B1. Retrieval boundary

**Decision:** EBE-005
**Status:** Completed

### Completed

- Introduced `RetrievalRequest`
- Introduced `RetrievalResult`
- Introduced `RetrievalService`
- Retrieval returns domain (`MemoryStone`) objects.
- Retrieval supports:
  - single entity
  - multi-entity union
- Retrieval is independently unit tested.

### Remaining

The query orchestrator still uses `graph_recall.py` as the production serialization path until the serialization layer is introduced.

### Follow-up

The retrieval layer intentionally returns ORM models rather than serialized API dictionaries.

### Acceptance criteria

- existing single-entity API behavior remains unchanged;
- query orchestrator no longer selects person/place/event retrieval itself;
- retrieval behavior has direct unit tests;
- full test suite remains green;
- no migration;
- no public API change unless separately approved.

---
## B2.1 Serialization Boundary

**Status:** Completed

### Goal

Separate retrieval from API serialization.

### Responsibilities

RetrievalService

- returns ORM models only
- performs no JSON serialization
- performs no response shaping

Serializer

- converts MemoryStone ORM models into API objects
- owns response serialization
- reusable by REST, CLI, LLM, and export pipelines

### Acceptance Criteria

- retrieval returns ORM objects only
- serializer owns MemoryStone serialization
- graph_recall uses serializer
- query_service no longer performs serialization

---
## B2.2 QueryService Retrieval Integration

**Status:** Completed

### Completed

- QueryService constructs typed `RetrievalRequest` objects;
- QueryService delegates database retrieval to `RetrievalService`;
- QueryService serializes results through the new transport boundary;
- QueryService no longer imports or dispatches through `graph_recall.py`;
- deterministic Memory Stone ordering is preserved;
- canonical-name and alias provenance is preserved;
- no database migration was required.

### Verification

```text
92 tests passing at completion
0 failures
```

## B3. Multi-entity resolution

**Status:** Completed
**Depends on:** B2.1

### Goal

Resolve every candidate phrase to a typed entity or explicit unresolved/ambiguous result.

Example:

```text
Tell me about Laura and Robert
```

becomes:

```text
Person: Laura
Person: Robert
```

### Required behavior

- preserve phrase order;
- retain match provenance;
- support aliases;
- expose unresolved phrases;
- expose ambiguous aliases;
- never silently drop a phrase.

### Open policy

Partial resolution may be:

- rejected;
- returned with warnings;
- allowed only for selected intents.

Preferred architecture: the planner or retrieval policy decides strictness based on intent.

### Acceptance criteria

- two canonical people resolve;
- aliases work;
- ambiguity is structured;
- unresolved phrases are explicit;
- single-entity behavior is unchanged.

---

## B3.1 Public Multi-Entity Response Contract

**Status:** Completed

### Completed

- added a dedicated multi-entity response schema;
- preserved the existing single-entity response schema;
- exposed ordered resolved entities and match provenance;
- labeled retrieval semantics as `entity_union`;
- enabled mixed person, place, and event queries;
- preserved alias provenance;
- retained strict all-or-nothing resolution;
- replaced the temporary HTTP 501 boundary.

### Current retrieval semantics

```text
direct memories for entity 1
+
direct memories for entity 2
+
direct memories for additional entities
    ↓
deduplicate by Memory Stone ID
    ↓
preserve first-seen order
```

This is union retrieval. It does not claim that every returned memory is shared by every resolved entity.

### Verification

```text
95 tests passing
0 failures
```

### Next

Generate deterministic graph-intersection and fallback plans.

---

## B4. Retrieval plan generation

**Status:** Planned
**Depends on:** B3

### Goal

Produce deterministic retrieval steps without executing the database.

Example:

```text
Robert + Laura + Art Museum
```

Exact step:

```text
Robert ∩ Laura ∩ Art Museum
```

Progressive fallback:

1. Robert + Laura + Art Museum
2. Robert + Laura
3. Laura + Art Museum
4. Robert + Art Museum
5. constrained semantic search
6. broad semantic search

### Required properties

- deterministic order;
- exact step first;
- no duplicate step combinations;
- every fallback has a level and reason;
- plan is unit-testable without a database.

---

## B5. Multi-entity graph execution

**Status:** Planned
**Depends on:** B4

### Goal

Execute graph intersections and pairwise fallbacks.

### Required behavior

- exact memory intersections;
- pairwise intersections;
- deduplication;
- stable ordering;
- result limits;
- strategy provenance;
- efficient SQL;
- no N+1 loading.

### Acceptance criteria

- exact shared memories return first;
- relaxed results are labeled;
- duplicate memories are removed;
- representative data-volume test passes;
- API contract remains stable.

---

## B6. Semantic fallback and graph-vector fusion

**Status:** Planned
**Depends on:** B5

### Goal

Use vector search when graph retrieval is insufficient, while preserving the distinction between explicit and associative evidence.

Preferred sequence:

```text
exact graph
→ relaxed graph
→ entity-constrained vector
→ broad vector
```

### Required behavior

- graph matches cannot be mislabeled as semantic;
- semantic matches cannot be presented as explicit relationships;
- ranker receives source and strategy metadata;
- fallback level is visible.

---

## B7. Response builder

**Status:** Planned
**Depends on:** B1–B6 as needed

### Goal

Move API-shape construction out of the query orchestrator.

Potential response fields:

```text
query
normalized_query
intent
entities
unresolved_phrases
retrieval_strategy
exact_match
fallback_level
memories
warnings
provenance
```

Any public response change requires a separate approved decision.

---

# Stage C — Rich Query Understanding

## C1. Expanded intent model

**Status:** Future

Candidate intents:

```text
entity_summary
shared_memory
relationship
timeline
location_history
event_history
semantic_recall
comparison
unknown
```

Start deterministic. Add model-backed classification only where deterministic confidence is insufficient.

## C2. Temporal interpretation

**Status:** Future

Examples:

```text
What happened after Christmas?
What happened before the memorial?
What did Laura do last summer?
Show memories from 2025 involving Robert.
```

Likely component:

```text
apps/api/app/services/query/temporal.py
```

Must handle:

- explicit dates;
- date ranges;
- relative dates;
- uncertain dates;
- before/after relations;
- timezone policy.

## C3. Relationship questions

**Status:** Future

Examples:

```text
How is Robert connected to Laura?
Where did Laura and I meet?
Who was at the wedding?
```

Requires:

- relationship-aware plans;
- path constraints;
- evidence-backed answers;
- path provenance.

## C4. Multi-hop graph expansion

**Status:** Future

This was considered earlier but deferred because the initial expansion draft did not match the existing graph-recall abstraction and because query orchestration should be established first.

Future multi-hop work should:

- use the retrieval planner;
- define maximum depth;
- prevent cycles;
- control result explosion;
- score path quality;
- expose traversal provenance.

---

# Stage D — Ranking and Grounded Answers

## D1. Unified ranking

**Status:** Future

Potential signals:

- exact entity intersection;
- number of matched entities;
- relationship path length;
- semantic similarity;
- importance;
- temporal relevance;
- user-confirmed status;
- source quality;
- contradiction or duplicate state.

The ranker should preserve raw signals.

## D2. Evidence bundle

**Status:** Future

Before asking a model to synthesize, construct a bounded bundle containing:

```text
resolved entities
selected memories
relationships
timeline
retrieval strategy
fallback level
source provenance
warnings
```

## D3. Narrative synthesis

**Status:** Future

The model may summarize only the evidence bundle.

Required safeguards:

- distinguish memory from inference;
- cite or reference the supporting memory stones;
- disclose uncertainty;
- do not infer accusations or motives without evidence;
- do not overwrite factual memory.

---

# Stage E — Biblical Context

## E1. Optional biblical enrichment

**Status:** Future and separately governed

### Product requirement

Biblical context may support reflection, encouragement, prayer, or analogy. It must remain optional and downstream from factual retrieval.

### Required safeguards

- clearly label interpretation;
- attach Scripture references;
- do not invent quotations;
- separate direct biblical teaching from analogy;
- do not convert biblical interpretation into factual memory;
- allow disabling;
- avoid intensifying guilt, fear, delusion, or interpersonal accusation.

Potential flow:

```text
retrieved factual evidence
    ↓
context policy
    ↓
biblical reference retrieval
    ↓
optional interpretation
```

---

# Stage F — Safety, Evaluation, and Operations

## F1. Evaluation suite

Measure:

- entity-resolution accuracy;
- alias ambiguity handling;
- graph-intersection correctness;
- semantic relevance;
- fallback disclosure;
- provenance completeness;
- contradiction handling;
- latency;
- hallucination resistance.

## F2. Observability

Record:

```text
query plan
resolved entities
retrieval steps
fallback step used
result count
execution time
warnings
user correction
```

Logs should minimize exposure of private memory content.

## F3. Privacy and authorization

Before multi-user or shared-family use:

- define memory ownership;
- define visibility;
- define delegation;
- define deletion;
- define export;
- define access to sensitive memories;
- ensure vector and graph paths honor authorization filters.

---

# Planned Near-Term Sequence

1. Complete serialization boundary
2. Integrate RetrievalService into QueryService
3. Retire graph_recall retrieval responsibilities
4. Generate retrieval plans
5. Execute graph intersections
6. Progressive graph fallback
7. Semantic fallback
8. Response builder
9. Expanded intents
10. Temporal reasoning
11. Relationship queries
12. Ranking
13. Evidence bundles
14. Optional grounded synthesis
15. Biblical enrichment
