# Validation

For new or regenerated source-range notes, follow the workspace's active authoring contract. Verify source identity, review evidence, exact current body, teaching requirements, and the final rendered artifacts; preserve historical notes and their recorded provenance.

For teaching-note validation, read [Teaching Foundations](../references/teaching-foundations.md) and the workspace's current teaching/page contracts. Deterministic structural validation does not prove understanding. Inspect independent coverage and teaching judgments, exact body evidence, dependency order, circular definitions, condition reasons, method choice, source-language mapping, supplements and prior recaps. Preserve concrete failed diagnostics; passing render or coverage cannot clear them.

Use for integrity checks, migration checks, stale state or retrieval-cache diagnosis.

1. Run the state helper’s validation/resume checks.
2. Run the workspace’s existing Canonical validation. Add PDF hash checks when source integrity or migration is in question.
3. Treat Index as derived: verify/rebuild it separately from Canonical validation.
4. If both Course Recall capability files exist, run the workspace's Course Recall validation and rebuild only when its derived inputs require it. If either file is absent, record the compatible Canonical-only mode and do not call a missing command.
5. Confirm that ordinary reading/solve state carries no review references, every `candidate_id` names a current pending candidate, and only Review/Knowledge Pack state carries pending review or pack references.
6. Classify confirmed problems by impact. P0/P1 may be handled immediately within authorization; record P2/P3 observations and collect recurrence evidence.
7. Do not auto-delete orphaned files, rewrite Source hashes, edit approval evidence or change Canonical content to silence an error.
8. Checkpoint the validation result and Index dirty state after meaningful checks.

For reader/annotation maintenance, read [personal annotations](../references/personal-annotations.md). Use isolated stores for browser acceptance; verify private/published hashes, old page marks, per-record conflicts, failure drafts, restart and conservative location/version isolation. Personal UI actions do not update study state.

For inline remarks, verify existing records appear beside content without opening lists, matching numbers for multiple marks, in-place read/edit/save, and readable unlocated evidence. After inserting or changing remarks, test subsequent source selection and new image/formula regions, including nonempty source context when available. Check editor input/focus/caret through background refresh and conflicts, and overlay alignment through remark-height changes, viewport reflow and actual browser zoom. Report a visual zoom pass only when its rendered alignment was observed.

Report exact errors/warnings and the next recoverable action under [User-Facing Delivery](../references/user-delivery.md). Use a readable conversation summary or a formatted report, not raw logs or Markdown; reveal technical paths or identifiers only when they are required for recovery. A missing external PDF is a portability issue when archived Captures and Canonical objects remain intact.

For source-region teaching, read `source-annotations-v1.3.md` and verify original PDF/image provenance, normalized region evidence, exact block mappings, first-use English, safe edge-attached numbers and unchanged originals. Retain independent schema-2 semantic coverage and teaching review; layout or geometry cannot pass either. Run the paired DOM and whole-slide printing path. Independently check one original per slide, no continuation images/crops, natural teaching flow, exact text/math and order preservation, readable type and actual PDF page counts. Reject missing print evidence or more than two pages; review density and explain indispensable teaching before any further layout choice. Review all points at the three specified MacBook windows, all PDF pages and isolated personal annotation compatibility. Report remaining failures honestly and keep unpassed outputs in Staging.
