# Workspace Contract

## Required layout

An Electrical Engineering KB workspace is identified by its root `AGENTS.md`, `VERSION`, `objects/`, `staging/`, `sources/`, `tools/`, and `00_System/runtime/CURRENT_STATE.yaml`.

The workspace owns private and project-specific data:

- `objects/`: Canonical Concept, Formula, Diagram, Data, Problem, and Insight objects;
- `sources/`: Source Registry and immutable Capture evidence;
- `staging/`: candidates, explanations, reviews, approvals, and uncommitted drafts;
- `publications/` and `explanations/`: publication evidence and archived explanations;
- `10_Reading/`: derived human presentation;
- `runtime/index.sqlite3`: derived local search cache;
- `tools/`: the workspace’s deterministic PDF and KB implementation;
- `00_System/runtime/`: current state and concise session history.

The Skill owns reusable behavior and state/source helper scripts. It must not contain object IDs, PDF names, course progress, private notes, or absolute user paths.

## Tool discovery

Run commands from the workspace root. Prefer `.venv/bin/python` when present, otherwise use a Python interpreter that satisfies the workspace’s documented dependencies. Inspect the local CLI help or `00_System/specs/cli-v1.md`; do not assume a future command exists merely because a workflow describes an outcome.

Typical deterministic interfaces are:

```text
<workspace-python> tools/pdf.py read|crop ...
<workspace-python> tools/kb.py create|show|update|link|unlink|publish|search|index|validate ...
<workspace-python> <skill-root>/scripts/state.py resume|validate|checkpoint --workspace <workspace>
<workspace-python> <skill-root>/scripts/rebind_source.py --workspace <workspace> ...
```

## Permission boundary

Codex may automatically read, search, inspect, validate, rebuild derived indexes, update runtime state, prepare Staging, and crop a target already approved by the user.

User approval must bind the exact review version before:

- creating new Canonical knowledge;
- publishing a new Insight;
- materially changing a Canonical explanation, conclusion, Trigger, Source, or major Relation;
- deleting formal knowledge or necessary evidence;
- performing a large classification or migration rewrite.

Mechanical formatting or state corrections may be made only when they preserve the already approved meaning and scope. Use the workspace’s safe revision path rather than direct edits to Canonical objects.

## Retrieval

For a new workspace problem, follow [Solve](../workflows/solve.md). When the workspace provides Course Recall, it locates relevant Reading and Source pages alongside approved Canonical Search results. Verify relevant original pages before using Reading-derived text as fact. When Course Recall is absent, use the Canonical-only route.

## Recovery

If state and workspace evidence disagree, the evidence wins: publication receipts determine whether a reviewed object was committed, Canonical Markdown determines current knowledge, and the rebuilt Index reflects Markdown. Correct state through a new checkpoint; do not rewrite evidence to match stale state.
