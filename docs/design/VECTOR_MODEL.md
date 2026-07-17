# Ebe Vector Model

## Purpose

The vector layer supports associative recall when wording and concepts differ.

It is useful for questions such as:

```text
What reminds me of Dad?
Show memories about feeling supported.
Find memories similar to this one.
```

## Current Role

- embed Memory Stones;
- compare a query embedding to stored embeddings;
- combine semantic relevance with importance;
- return ranked semantic candidates.

## Limits

Vector similarity does not establish:

- identity;
- explicit participation;
- exact location;
- exact event membership;
- chronology;
- truth.

## Future Hybrid Policy

Preferred sequence:

```text
exact graph evidence
→ relaxed graph evidence
→ entity-constrained vector evidence
→ broad vector evidence
```

Every candidate should retain:

- semantic score;
- retrieval score;
- importance;
- strategy;
- constraints used.

## Authorization

Vector queries must apply the same future ownership and visibility filters as relational queries. Embedding search must not become a path around access control.
