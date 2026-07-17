# Ebe Engineering Style Guide

## Python

- Use type annotations for service boundaries.
- Prefer immutable dataclasses for plans and internal request objects.
- Keep orchestration functions short.
- Keep database queries in retrieval or repository-oriented services.
- Avoid `dict` as a long-term internal contract when a typed model improves clarity.
- Do not create parallel abstractions with different names for the same concept.
- Use existing serializers unless a decision approves a new response boundary.
- Preserve clear FastAPI status behavior.
- Prefer explicit ambiguity over arbitrary `.first()` selection.

## Imports

Order:

1. standard library;
2. third-party;
3. application imports.

Use:

```python
from typing import Any
```

not:

```python
from typing import any
```

## Routes

- Decorators and route functions remain at module scope.
- Verify registration through OpenAPI.
- Routers delegate business behavior to services.
- Do not duplicate retrieval logic in routes.

## Services

A service should have one primary reason to change.

Examples:

```text
normalizer → text cleanup rules
planner → query intent and candidate plan
resolver → identity matching
retrieval → evidence acquisition
ranker → result ordering
response builder → public representation
```

## Tests

- Assert the public behavior that matters.
- Use `pytest.approx` for computed floating-point values.
- Keep assertions inside their test function.
- Do not weaken a correct test to hide a registration or implementation defect.

## Documentation

- Proposed work stays Proposed.
- Record proposer and approver.
- Add a superseding entry rather than rewriting decision history.
- Mark Completed only after verification.
