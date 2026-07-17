# Ebe Human-Readable Changelog

This is not a replacement for Git history. It explains the architectural evolution in product terms.

## 2026-07-17

### Added engineering notebook

Created durable documentation for:

- current state;
- roadmap;
- decisions and approval history;
- milestones;
- architecture;
- development workflow;
- testing;
- graph, vector, memory, and query design.

### Recorded current query boundary

Documented that single-entity queries are implemented and multi-entity queries are explicitly rejected with HTTP 501 until retrieval support exists.

### Proposed retrieval-engine boundary

Recorded EBE-005 as proposed, not approved.

---

## Historical development sequence

### Storage phase

Ebe gained:

- Memory Stone persistence;
- people, places, and events;
- relationships;
- extraction and review.

### Associative recall phase

Ebe gained:

- embeddings;
- semantic search;
- importance-aware ranking.

### Knowledge-graph recall phase

Ebe gained:

- person recall;
- place recall;
- event recall;
- person timeline;
- person context.

### Query phase

Ebe gained:

- natural-language query normalization;
- canonical and alias resolution;
- provenance;
- a modular planner;
- an explicit boundary for unfinished multi-entity behavior.

### Current transition

Ebe is transitioning from entity-specific query orchestration to a general retrieval pipeline capable of graph intersections, semantic fallback, temporal constraints, ranking, and grounded synthesis.
