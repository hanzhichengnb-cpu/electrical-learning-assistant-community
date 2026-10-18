# Portability and Source Rebinding

## Skill

The `electrical-learning-assistant-community/` folder contains the reusable Skill source, not learner progress. It may be stored in its own Git repository and installed under the target Codex skill directory. Installation location is environment-specific and must not be written into workspace state.

## Workspace

The workspace may move by Git, iCloud, or ordinary directory copy. Markdown objects, IDs, Relations, Captures, publication receipts, Reading Notes, Runtime State, and Session Log remain useful immediately. `runtime/index.sqlite3` may be discarded and rebuilt from Canonical Markdown.

The workspace must not store an absolute active path in `CURRENT_STATE.yaml`. Source Registry locations use `{base: kb_root, path: <relative-path>}`.

## Machine-specific historical fields

Capture manifests may contain `source_path_observed` and `source_record_path_observed`. These are immutable audit observations from extraction time, not active locators. Do not rewrite old Capture packages during migration.

The active locator is the matching Source Registry version’s `locations` list. Old relative locations may become unavailable after a move without damaging Canonical knowledge or archived Captures.

## Minimal rebind

Use `scripts/rebind_source.py` with a Source ID and an existing PDF. The script:

1. hashes the selected PDF;
2. requires the hash to match an existing registered Source version;
3. adds a workspace-relative location atomically;
4. preserves the previous registry under `00_System/runtime/source-registry-backups/`, outside the formal Source Registry scan;
5. never rewrites Canonical objects or Capture manifests.

It refuses a hash mismatch. Registering a genuinely new PDF version remains a separate Source workflow.

After rebinding, run workspace validation with PDF hashes and rebuild the Index only if Canonical Markdown changed or the copied Index is absent/stale.
