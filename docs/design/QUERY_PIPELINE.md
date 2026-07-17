# Ebe Query Pipeline

## Current Pipeline

```text
Request
  ↓
normalize_query
  ↓
create_query_plan
  ↓
resolve_single_entity
  ↓
graph recall
  ↓
response
```

## Current Supported Intent

```text
single_entity
```

The planner can detect a simple `multi_entity` structure, but retrieval is not implemented and returns HTTP 501.

## Target Pipeline

```text
Raw query
  ↓
NormalizedQuery
  ↓
QueryPlan
  ↓
Resolved entities
  ↓
RetrievalPlan
  ↓
RetrievalResult
  ↓
Ranked evidence
  ↓
Public response
  ↓
Optional synthesis
```

## Proposed Internal Types

```python
@dataclass(frozen=True)
class QueryPlan:
    intent: QueryIntent
    query_text: str
    candidate_phrases: tuple[str, ...]
```

```python
@dataclass(frozen=True)
class ResolvedEntity:
    entity_type: EntityType
    entity: Person | Place | Event
    matched_by: MatchType
    matched_value: str
```

```python
@dataclass(frozen=True)
class RetrievalRequest:
    plan: QueryPlan
    resolved_entities: tuple[ResolvedEntity, ...]
```

Potential future models:

```python
@dataclass(frozen=True)
class RetrievalStep:
    strategy: str
    entity_keys: tuple[str, ...]
    priority: int
```

```python
@dataclass(frozen=True)
class RetrievalResult:
    strategy: str
    exact_match: bool
    fallback_level: int
    memories: tuple[object, ...]
    warnings: tuple[str, ...]
```

These are design directions, not approved final schemas.

## Error Policy

- empty query: validation error;
- no entity: not found or unresolved response;
- ambiguous identity: conflict or disambiguation response;
- unsupported intent: explicit unsupported status;
- fallback result: success with disclosed strategy, not a fabricated exact match.
