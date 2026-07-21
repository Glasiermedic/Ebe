# Ebe Decision Log

**Updated:** 2026-07-19 America/Los_Angeles

This file is append-oriented. Do not silently rewrite a completed or rejected decision to make history appear cleaner. Add a new entry that supersedes the prior decision.

---

## EBE-001 — Separate query normalization and entity resolution

**Type:** Architecture
**Recorded:** 2026-07-17 as a historical entry
**Proposed by:** ChatGPT
**Reviewed by:** Wesley
**Approved by:** Wesley
**Status:** Completed

### Context

The initial query service was beginning to combine conversational text handling, identity lookup, and retrieval.

### Decision

Keep `query_service.py` as an orchestrator and create focused modules under:

```text
app/services/query/
```

including normalization and entity resolution.

### Rationale

Smaller components lower regression risk and make later multi-entity and intent-aware behavior easier to add.

### Alternatives

- keep all behavior in `query_service.py`;
- replace the entire query layer immediately;
- introduce advanced model-based planning before stable deterministic components.

### Acceptance

- single-entity behavior preserved;
- aliases preserved;
- tests green.

### Impact

- **API:** None intended
- **Database:** None
- **Supersedes:** Informal monolithic query-service direction

---

## EBE-002 — Add a repository snapshot utility

**Type:** Development Process
**Recorded:** 2026-07-17 as a historical entry
**Proposed by:** Wesley
**Reviewed by:** ChatGPT
**Approved by:** Wesley
**Status:** Completed

### Context

Architectural suggestions risked duplicating existing files or using abstractions that no longer matched the repository.

### Decision

Maintain a reusable repository inventory script.

### Rationale

The script creates a common view of:

- files;
- routes;
- classes;
- functions;
- schemas;
- query-related imports;
- tests;
- Git status.

### Acceptance

- runs from the project;
- excludes `__pycache__`;
- identifies query-related modules;
- can be pasted into a development conversation.

### Impact

- **API:** None
- **Database:** None

---

## EBE-003 — Add a pure initial query planner

**Type:** Architecture
**Recorded:** 2026-07-17 as a historical entry
**Proposed by:** ChatGPT
**Reviewed by:** Wesley
**Approved by:** Wesley
**Status:** Completed

### Decision

Add a deterministic planner that identifies:

```text
single_entity
multi_entity
unknown
```

and returns candidate phrases without database access.

### Rationale

Planning is distinct from normalization, identity resolution, and retrieval.

### Acceptance

- single query produces one candidate;
- simple conjunction produces multiple candidates;
- empty input becomes unknown;
- dedicated tests pass.

### Impact

- **API:** None at isolated-module stage
- **Database:** None

---

## EBE-004 — Integrate the planner and reject unfinished multi-entity retrieval explicitly

**Type:** Product + Architecture
**Recorded:** 2026-07-17 as a historical entry
**Proposed by:** ChatGPT
**Reviewed by:** Wesley
**Approved by:** Wesley
**Status:** Completed

### Decision

Route normalized requests through the planner.

For `multi_entity`, return HTTP 501 with candidate phrases until the feature is truly implemented.

### Rationale

Ebe must not silently answer only the first entity or misrepresent a partial result as complete.

### Acceptance

- existing single-entity tests pass;
- multi-entity request returns 501;
- candidate phrases are present;
- full suite passes.

### Impact

- **API:** Explicit 501 behavior added for multi-entity input
- **Database:** None
- **Future:** Superseded when multi-entity retrieval is completed

---

## EBE-005 — Establish a retrieval boundary and request model

**Type:** Architecture
**Created:** 2026-07-17 11:01 America/Los_Angeles
**Proposed by:** ChatGPT
**Reviewed by:** Pending
**Approved by:** Pending
**Status:** Proposed

### Context

The query orchestrator still branches by entity type and directly selects graph-recall functions.

That is retrieval behavior rather than orchestration.

### Proposal

Create:

```text
app/services/query/retrieval.py
```

and introduce a typed request object resembling:

```python
@dataclass(frozen=True)
class RetrievalRequest:
    plan: QueryPlan
    resolved_entities: tuple[ResolvedEntity, ...]
```

A retrieval result should eventually carry:

```text
memories
strategy
exact_match
fallback_level
warnings
```

### Rationale

A stable request object can absorb future needs without repeatedly changing function signatures:

- graph intersections;
- vector fallback;
- time windows;
- SQL filters;
- confidence;
- ranking;
- provenance.

### Alternatives

1. Keep `_retrieve_entity_memories()` in `query_service.py`.
2. Move only the helper function without introducing a request object.
3. Implement multi-entity retrieval first.
4. Move branching into `graph_recall.py`.

### Proposed decision

Extract retrieval behind one service boundary while preserving all public behavior.

### Acceptance

- current API output unchanged;
- direct retrieval unit tests added;
- orchestrator no longer branches by entity type;
- no migration;
- full suite green.

### Impact

- **API:** None intended
- **Database:** None intended
- **Implementation:** Do not begin until Wesley approves

---

## EBE-006 — Adopt a durable engineering notebook

**Type:** Development Process
**Created:** 2026-07-17 11:01 America/Los_Angeles
**Proposed by:** Wesley
**Reviewed by:** ChatGPT
**Approved by:** Wesley
**Status:** Approved

### Context

Important planning decisions, implementation corrections, and approval history were scattered across chat transcripts.

### Decision

Store a living engineering notebook in the repository containing:

- current state;
- roadmap;
- decisions;
- milestones;
- architecture;
- changelog;
- open questions;
- development workflow;
- testing rules;
- design documents.

### Rationale

The repository should preserve:

- what changed;
- who suggested it;
- who approved it;
- why it changed;
- what was verified;
- what remains proposed.

### Acceptance

- documents exist under `docs/`;
- proposed and approved work are distinct;
- decisions record authorship and acceptance;
- future material changes receive entries;
- completed work records tests or other verification.

### Impact

- **API:** None
- **Database:** None
- **Supersedes:** Conversation-only planning

---

## EBE-007 — Inspect existing abstractions before implementing suggested code

**Type:** Development Process
**Created:** 2026-07-17 11:01 America/Los_Angeles
**Proposed by:** ChatGPT, based on implementation history
**Reviewed by:** Wesley through repeated use of inspection-first workflow
**Approved by:** Wesley
**Status:** Approved

### Context

During graph-expansion planning, a proposed helper used parameter names and assumptions that did not match the existing generic graph-recall abstraction. Router work also showed that code could be syntactically correct in isolation while not being registered or placed at module scope.

### Decision

Before substantial code changes:

1. run the snapshot;
2. inspect the target file;
3. inspect the relevant tests and schemas;
4. edit only the required section;
5. verify route registration where applicable;
6. run focused checks before the full suite.

### Rationale

This reduces:

- duplicate abstractions;
- incompatible helper signatures;
- accidental file replacement;
- route-registration errors;
- stale assumptions;
- unnecessary rework.

### Acceptance

The workflow is documented in `docs/developer/DEVELOPMENT_WORKFLOW.md`.

### Impact

- **API:** None
- **Database:** None

---

## EBE-008 — Defer unrestricted multi-hop graph expansion until retrieval planning exists

**Type:** Architecture
**Created:** 2026-07-17 11:01 America/Los_Angeles
**Proposed by:** ChatGPT after reviewing the existing graph-recall abstraction
**Reviewed by:** Wesley
**Approved by:** Inferred from proceeding to the query layer; confirm if desired
**Status:** Approved with confirmation recommended

### Context

An early proposal attempted to add expanded memories directly to person context. The draft did not match the established `_get_related_memories()` abstraction, and future semantic retrieval would likely change expansion strategy.

### Decision

Complete query orchestration and retrieval planning before introducing generalized multi-hop graph expansion.

### Rationale

Multi-hop expansion needs:

- depth policy;
- cycle protection;
- ranking;
- result limits;
- fallback policy;
- provenance.

Those belong in a retrieval architecture rather than directly inside a person-context response.

### Impact

- **API:** Avoids premature context-schema expansion
- **Database:** None
- **Open point:** Wesley may explicitly confirm or revise this historical interpretation


## ADR-0007 — Separate Retrieval From Serialization

**Type:** Architecture
**Created:** 2026-07-19
**Proposed by:** ChatGPT after inspection of `graph_recall.py`
**Reviewed by:** Wesley
**Approved by:** Wesley
**Status:** Accepted

### Context

During implementation of multi-entity retrieval we discovered that graph_recall.py combined:

- SQL graph traversal
- result ordering
- JSON serialization
- timeline generation
- context generation

Migrating all of this into RetrievalService would violate single-responsibility principles.

### Decision

RetrievalService will return ORM models only.

Serialization will become its own pipeline stage.

graph_recall.py will remain temporarily until serialization is migrated.

### Consequences

#### Pros

- cleaner architecture
- reusable retrieval engine
- easier testing
- easier ranking implementation
- easier semantic retrieval
- easier Graph + Vector integration

#### Cons

- temporary duplication during migration

---

## EBE-009 — Complete the foundational retrieval boundary

**Type:** Architecture + Implementation
**Created:** 2026-07-19
**Proposed by:** ChatGPT
**Reviewed by:** Wesley
**Approved by:** Wesley
**Status:** Completed

### Context

EBE-005 proposed a typed retrieval boundary. Subsequent implementation added immutable request/result contracts, ordered multi-entity resolution, and a dedicated retrieval service.

### Decision

Accept the foundational retrieval boundary as implemented:

- `RetrievalRequest` and `RetrievalResult` are immutable contracts;
- `resolve_entities()` resolves every candidate phrase in order;
- unresolved phrases currently fail strictly with HTTP 404;
- `RetrievalService` returns `MemoryStone` ORM/domain objects;
- zero-, single-, and multi-entity requests are supported;
- multi-entity retrieval currently uses union semantics;
- duplicate Memory Stones are removed by ID;
- first-seen ordering is preserved.

### Verification

- resolver tests cover canonical names, aliases, missing positions, mixed entity types, and order preservation;
- retrieval tests cover person, place, event, empty results, zero entities, union retrieval, mixed entities, and deduplication;
- full suite reported green with 83 passing tests.

### Impact

- **API:** No production API integration yet
- **Database:** None
- **Supersedes:** EBE-005 as a pending proposal
- **Next:** Implement ADR-0007 serializer boundary before QueryService integration

## EBE-010 — Separate relationship loading from Memory Stone serialization

**Type:** Architecture + Implementation
**Created:** 2026-07-21
**Proposed by:** ChatGPT
**Reviewed by:** Wesley
**Approved by:** Wesley
**Status:** Completed

### Decision

Separate the responsibilities into:

```text
MemoryStone ORM objects
    ↓
batch relationship loader
    ↓
immutable relationship bundles
    ↓
pure serializer
```

The pure serializer accepts no database session and executes no SQL. Relationship metadata is loaded using three queries per Memory Stone collection.

### Impact

- **API:** Existing response shape preserved
- **Database:** No migration
- **Performance:** Three relationship queries per collection instead of per Memory Stone
- **Verification:** Full suite green

---

## EBE-011 — Integrate RetrievalService into QueryService

**Type:** Architecture + Implementation
**Created:** 2026-07-21
**Proposed by:** ChatGPT
**Reviewed by:** Wesley
**Approved by:** Wesley
**Status:** Completed

### Decision

Migrate the production single-entity query path to:

```text
Resolver
    ↓
RetrievalRequest
    ↓
RetrievalService
    ↓
batch relationship loader
    ↓
pure serializer
```

### Compatibility

- existing single-entity response behavior preserved;
- canonical-name and alias provenance preserved;
- deterministic ordering preserved;
- no database migration.

### Verification

```text
92 tests passing at completion
0 failures
```

---

## EBE-012 — Approve the public multi-entity query response contract

**Type:** Product + Architecture + Implementation
**Created:** 2026-07-21
**Proposed by:** ChatGPT
**Reviewed by:** Wesley
**Approved by:** Wesley
**Status:** Completed

### Decision

Add a separate multi-entity response containing:

```text
query
normalized_query
intent
entities
retrieval_strategy
memories
```

Each resolved entity retains its type and match provenance. The initial strategy is explicitly labeled `entity_union`.

### Resolution policy

- all candidate phrases must resolve;
- unresolved candidates return HTTP 404;
- the failed candidate phrase is disclosed;
- ambiguous aliases return HTTP 409;
- partial results are not returned;
- no candidate is silently dropped.

### Verification

```text
95 tests passing
0 failures
```

### Next

Implement deterministic retrieval-plan generation for exact intersections and progressive graph fallback.
