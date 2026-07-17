# Ebe Development Workflow

## Session Start

```bash
cd ~/projects/ebe/apps/api

git status
git branch

docker ps

uv run alembic current
uv run alembic heads

uv run ruff check app migrations tests
uv run python -m compileall app migrations tests
uv run pytest -v
```

Expected state:

- correct branch;
- PostgreSQL running;
- Alembic current equals heads;
- lint green;
- compile green;
- tests green.

Then inspect the roadmap:

```bash
cd ~/projects/ebe

sed -n '1,240p' docs/roadmap/CURRENT_STATE.md
sed -n '1,260p' docs/roadmap/ROADMAP.md
grep -n "Status: Proposed\|Status: Approved\|Status: In Progress"     docs/roadmap/DECISIONS.md
```

Run the project snapshot:

```bash
./apps/api/scripts/project_snapshot.sh
```

or:

```bash
./scripts/project_snapshot.sh
```

Use whichever location exists, then update `CURRENT_STATE.md` so the documented path is canonical.

---

## Before Coding

1. Identify the roadmap item and decision ID.
2. Confirm the decision is Approved.
3. Inspect current files, schemas, routes, tests, and imports.
4. Confirm the proposed abstraction matches existing parameter names and types.
5. Define focused acceptance criteria.
6. Avoid replacing an entire file when a targeted edit is safer.

---

## Implementation Loop

```text
Inspect
  ↓
Make one coherent change
  ↓
Format
  ↓
Lint focused files
  ↓
Compile if imports or syntax changed
  ↓
Run focused tests
  ↓
Inspect failure category
  ↓
Fix implementation or test
  ↓
Run full suite
```

### Focused validation example

```bash
uv run ruff format     app/services/query/retrieval.py     app/services/query/models.py     tests/test_query_retrieval.py

uv run ruff check     app/services/query/retrieval.py     app/services/query/models.py     tests/test_query_retrieval.py

uv run pytest tests/test_query_retrieval.py -v
```

### Full validation

```bash
uv run ruff check app migrations tests
uv run python -m compileall app migrations tests
uv run pytest -v
```

---

## Failure Classification

Before changing code, identify the failure class.

### Import or collection failure

Examples:

- missing class;
- incorrect import;
- circular import;
- syntax error.

Do not debug runtime behavior until test collection succeeds.

### Plain FastAPI 404

```json
{"detail": "Not Found"}
```

This usually means no route matched. Check:

- router imported in `app/main.py`;
- router included;
- route decorator at module scope;
- path and prefix;
- OpenAPI registration.

### Service-level 404

```json
{"detail": "Person not found"}
```

This means the route matched and the service executed.

### Ruff undefined names in tests

Often indicates:

- assertions accidentally outside the test function;
- indentation problem;
- variable renamed or removed.

### Floating-point failure

Use approximate comparison where appropriate:

```python
assert score == pytest.approx(0.83)
```

### Stale or unsaved file suspicion

Re-read the file from disk:

```bash
nl -ba path/to/file.py
```

Then rerun Ruff. Do not rely on what the editor appears to show.

---

## Route Verification

After adding an endpoint:

```bash
uv run python - <<'PY'
from app.main import app

path = "/expected/path"

print(f"{path} registered:", path in app.openapi()["paths"])
PY
```

When iterating raw routes, use `getattr` because not every route-like object necessarily exposes the same attributes:

```python
for route in app.routes:
    path = getattr(route, "path", None)
    if path:
        print(getattr(route, "methods", None), path)
```

---

## Commit Workflow

Commit only after the relevant acceptance criteria pass.

```bash
cd ~/projects/ebe

git status
git diff --stat
git diff

git add <intentional paths>
git commit -m "Describe completed capability"
git status
```

Push coherent green milestones:

```bash
git push origin main
```

After commit:

- update decision status to Completed;
- add verification and commit hash;
- update `MILESTONES.md`;
- update `CURRENT_STATE.md`;
- update `CHANGELOG.md`.

---

## Session End

A development session should leave:

- known test state;
- Git status recorded;
- current task status updated;
- newly proposed work marked Proposed;
- unfinished work marked In Progress or Blocked;
- next action written in `CURRENT_STATE.md`.
