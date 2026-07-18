#!/usr/bin/env bash

set -u

PROJECT_ROOT="${1:-.}"

cd "$PROJECT_ROOT" || exit 1

section() {
    echo
    echo "=================================================="
    echo "$1"
    echo "=================================================="
}

section "PROJECT FILES"

find app \
    -type d -name "__pycache__" -prune -o \
    -type f \
    \( -name "*.py" -o -name "*.sql" \) \
    -print \
    | sort

section "SERVICE MODULES"

find app/services \
    -type d -name "__pycache__" -prune -o \
    -type f -name "*.py" \
    -print \
    | sort

section "ROUTER MODULES"

find app/routers \
    -type d -name "__pycache__" -prune -o \
    -type f -name "*.py" \
    -print \
    | sort

section "ROUTES"

while IFS= read -r file; do
    matches="$(
        grep -nE \
            '^[[:space:]]*@router\.(get|post|put|patch|delete)\(' \
            "$file" 2>/dev/null || true
    )"

    if [[ -n "$matches" ]]; then
        echo
        echo "--- $file"
        echo "$matches"
    fi
done < <(
    find app/routers \
        -type d -name "__pycache__" -prune -o \
        -type f -name "*.py" \
        -print \
        | sort
)

section "CLASSES BY FILE"

while IFS= read -r file; do
    matches="$(
        grep -nE \
            '^[[:space:]]*class[[:space:]]+[A-Za-z_][A-Za-z0-9_]*' \
            "$file" 2>/dev/null || true
    )"

    if [[ -n "$matches" ]]; then
        echo
        echo "--- $file"
        echo "$matches"
    fi
done < <(
    find app \
        -type d -name "__pycache__" -prune -o \
        -type f -name "*.py" \
        -print \
        | sort
)

section "FUNCTIONS BY FILE"

while IFS= read -r file; do
    matches="$(
        grep -nE \
            '^[[:space:]]*(async[[:space:]]+)?def[[:space:]]+[A-Za-z_][A-Za-z0-9_]*' \
            "$file" 2>/dev/null || true
    )"

    if [[ -n "$matches" ]]; then
        echo
        echo "--- $file"
        echo "$matches"
    fi
done < <(
    find app \
        -type d -name "__pycache__" -prune -o \
        -type f -name "*.py" \
        -print \
        | sort
)

section "QUERY PIPELINE"

for file in \
    app/routers/query.py \
    app/services/query_service.py \
    app/services/query/models.py \
    app/services/query/normalizer.py \
    app/services/query/entity_resolver.py \
    app/services/query/planner.py \
    app/services/query/retrieval.py \
    app/services/query/response_builder.py
do
    if [[ -f "$file" ]]; then
        echo
        echo "--- $file"

        grep -nE \
            '^[[:space:]]*(class|async[[:space:]]+def|def)[[:space:]]+' \
            "$file" 2>/dev/null || true
    fi
done

section "IMPORT REFERENCES TO QUERY SERVICES"

grep -RInE \
    --exclude-dir="__pycache__" \
    --include="*.py" \
    'app\.services\.query|app\.services\.query_service' \
    app tests 2>/dev/null || true

section "TEST FILES"

if [[ -d tests ]]; then
    find tests \
        -type d -name "__pycache__" -prune -o \
        -type f -name "test_*.py" \
        -print \
        | sort
else
    echo "No tests directory found."
fi

section "GIT STATUS"

git status --short 2>/dev/null || echo "Not inside a Git repository."

section "DONE"
