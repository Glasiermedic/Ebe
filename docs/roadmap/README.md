# Roadmap Governance

The roadmap directory contains the canonical planning record for Ebe.

| File | Purpose |
|---|---|
| `CURRENT_STATE.md` | Fast orientation at the beginning of a development session |
| `ROADMAP.md` | Current approved and proposed implementation plan |
| `DECISIONS.md` | Append-oriented architecture and product decision history |
| `MILESTONES.md` | Completed vertical slices and the capabilities they unlocked |
| `CHANGELOG.md` | Human-readable chronological project evolution |
| `ARCHITECTURE.md` | Current architectural boundaries and target pipeline |
| `OPEN_QUESTIONS.md` | Decisions that are not yet resolved |
| `ENTRY_TEMPLATE.md` | Standard decision-entry format |

## Required update events

Update these documents when:

- a roadmap item is proposed, approved, rejected, blocked, completed, or superseded;
- implementation reveals that the current plan is incompatible with the repository;
- an API contract, data model, migration, retrieval strategy, ranking policy, or safety boundary changes;
- tests expose a meaningful design constraint;
- a completed milestone creates a new stable system capability.

## Source-of-truth hierarchy

When documentation conflicts:

1. Running code and migrations describe what exists.
2. Automated tests describe verified behavior.
3. `CURRENT_STATE.md` describes the latest known state.
4. Approved entries in `DECISIONS.md` describe intent.
5. `ROADMAP.md` describes planned future work.
6. Chat history is supporting context, not the canonical project record.
