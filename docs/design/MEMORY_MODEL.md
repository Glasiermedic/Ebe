# Ebe Memory Model

## Memory Stone

A Memory Stone is the primary stored unit of recollection.

It may contain:

- title;
- narrative content;
- remembered date;
- creation and update timestamps;
- importance;
- review state;
- extraction metadata;
- embedding;
- linked people;
- linked places;
- linked events;
- future source references.

A Memory Stone is factual user-provided or user-approved memory content. Later summaries or biblical interpretations should not silently become part of the original factual memory.

## Entities

### Person

Represents a canonical identity.

Includes aliases to support names such as:

```text
Laura
Sweets
Mom
```

Aliases are identity-resolution evidence, not separate people.

### Place

Represents a named location or setting.

### Event

Represents an occurrence or organized context that may connect several memories.

## Relationships

The current core graph is:

```text
Person ↔ Memory Stone
Place  ↔ Memory Stone
Event  ↔ Memory Stone
```

Relationship metadata should remain meaningful enough to distinguish concepts such as:

```text
subject
participant
location
part_of
```

## Provenance

Future memory evidence should be able to answer:

- who entered it;
- whether it was extracted;
- whether a user confirmed it;
- which source artifact supports it;
- which entities were linked automatically or manually;
- whether it has been corrected.

## Uncertainty

Do not force uncertain recollections into false precision.

Future model support may need:

- approximate date;
- date range;
- uncertain entity link;
- confidence;
- contradiction;
- alternate account.
