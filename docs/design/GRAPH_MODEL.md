# Ebe Graph Model

## Current One-Hop Graph

```text
Person
  ↓
Memory Stone
  ↑
Place

Event
  ↑
Memory Stone
```

Current deterministic recall retrieves memory stones directly connected to one entity.

## Person Context

Person context expands one hop through the person's direct memories to collect:

- related people;
- related places;
- related events.

This is bounded composition, not unrestricted graph traversal.

## Future Multi-Entity Intersection

Example:

```text
Laura ∩ Robert
```

returns memories explicitly linked to both.

Example:

```text
Laura ∩ Art Museum
```

returns memories linked to the person and place.

## Future Multi-Hop Traversal

Multi-hop traversal must define:

- maximum depth;
- allowed edge types;
- cycle detection;
- result limits;
- path scoring;
- privacy filters;
- provenance.

It should not be added as an unbounded recursive search.

## Graph Evidence

A graph match means an explicit stored relationship exists.

It does not necessarily prove:

- causation;
- emotional meaning;
- the user's interpretation;
- that every linked person participated equally.

Response construction must preserve that distinction.
