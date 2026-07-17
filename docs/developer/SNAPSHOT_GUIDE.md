# Project Snapshot Guide

## Purpose

The snapshot is an inspection tool used before architectural changes.

It should show enough of the current repository to prevent:

- duplicate modules;
- stale assumptions;
- incompatible helper signatures;
- missing tests;
- accidental router or schema duplication.

## Recommended output

- project tree excluding caches;
- routes;
- Pydantic schemas;
- SQLAlchemy models;
- classes and functions grouped by file;
- query pipeline modules;
- imports of query services;
- tests;
- migrations;
- Git branch and status.

## Usage

From the repository root:

```bash
./apps/api/scripts/project_snapshot.sh
```

or the current canonical script path.

## Updating the script

A script change should remain lightweight. Do not turn the snapshot into a static architecture source of truth. Its purpose is to inspect running repository state, while the engineering notebook explains intent and history.
