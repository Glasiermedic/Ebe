# Ebe Retrieval Design

## Retrieval Responsibilities

Retrieval answers:

```text
Given a query plan and resolved entities, which memory evidence should be returned?
```

It does not answer:

- how to normalize text;
- how to resolve names;
- how to phrase the final narrative.

## Initial Retrieval Strategies

```text
single_person
single_place
single_event
```

## Future Strategies

```text
person_person_intersection
person_place_intersection
person_event_intersection
multi_entity_intersection
pairwise_fallback
entity_constrained_semantic
broad_semantic
timeline_filter
relationship_path
```

## Progressive Fallback

For three entities:

```text
A + B + C
```

attempt:

1. A ∩ B ∩ C
2. A ∩ B
3. A ∩ C
4. B ∩ C
5. constrained semantic retrieval
6. broad semantic retrieval

The planner must define the order. The executor must report the successful step.

## Exactness

`exact_match` should mean the result satisfied the requested structural constraints, not merely that the title or text looked similar.

## Deduplication

The same Memory Stone may be found by several strategies. Preserve the best or strongest evidence while retaining all relevant provenance internally.

## Performance

Before scale:

- inspect SQL;
- index association foreign keys;
- avoid N+1 serialization;
- filter relationally before broad vector operations when possible;
- define result limits;
- measure representative data volumes.
