# Ebe Testing Strategy

## Principles

1. Test each layer directly.
2. Keep pure planning tests database-free.
3. Use database-backed tests for resolution and retrieval.
4. Use router integration tests for public response contracts.
5. Add a regression test for every fixed defect where practical.
6. Never mark a roadmap item Completed based only on manual testing.

---

## Test Layers

### Pure unit tests

Targets:

- normalization;
- candidate splitting;
- retrieval plan generation;
- score calculation;
- ranking rules.

Expected properties:

- fast;
- deterministic;
- no database;
- no network.

### Database-backed service tests

Targets:

- entity and alias resolution;
- graph intersections;
- retrieval execution;
- deduplication;
- time filters.

### Router integration tests

Targets:

- status codes;
- public schemas;
- validation;
- error details;
- provenance.

### Migration tests

At minimum:

- `alembic current`;
- `alembic heads`;
- upgrade from the supported prior revision where practical.

---

## Suggested Query Test Organization

```text
tests/test_query_normalizer.py
tests/test_query_planner.py
tests/test_entity_resolver.py
tests/test_query_retrieval.py
tests/test_query_response_builder.py
tests/test_query.py
```

Do not force this exact split if the current repository uses a different coherent convention. Inspect first.

---

## Required Commands

Focused:

```bash
uv run ruff check <changed files>
uv run pytest <focused tests> -v
```

Full:

```bash
uv run ruff check app migrations tests
uv run python -m compileall app migrations tests
uv run pytest -v
```

---

## Retrieval Test Matrix

### Single entity

- person by canonical name;
- person by alias;
- place;
- event;
- missing entity;
- ambiguous alias.

### Multi entity

- person + person;
- person + place;
- person + event;
- place + event;
- three entities;
- unresolved phrase;
- one ambiguous phrase;
- duplicate phrase;
- same entity referenced by canonical name and alias.

### Fallback

- exact intersection found;
- exact empty, pairwise found;
- graph empty, constrained semantic found;
- no acceptable result;
- fallback level disclosed;
- duplicate memory removed.

### Time

- before;
- after;
- bounded range;
- missing `remembered_at`;
- equal timestamps;
- timezone edge.

### Provenance

- canonical name;
- alias;
- graph strategy;
- vector strategy;
- fallback level;
- unresolved phrases;
- warnings.

---

## API Contract Policy

Any changed response field requires:

- schema update;
- router integration test;
- compatibility decision;
- changelog entry;
- client-impact note.

Internal refactors should preserve the public contract by default.
