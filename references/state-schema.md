# Runtime State Schema

`00_System/runtime/CURRENT_STATE.yaml` is the authority for “where work is now.” It stores references and status, not knowledge prose or conversation history.

## Required top-level fields

```yaml
schema_version: 1
state_revision: 1
workspace_id: <stable workspace identifier>
workspace_version: <current workspace VERSION>
skill:
  name: electrical-learning-assistant
  contract_version: 1
active_session: <session name or null>
current_mode: focus | review | solve | reflect | maintenance | idle
active_source: <mapping or null>
active_chapter: <short string or null>
active_topic: <short string or null>
current_pdf_page: <mapping or null>
active_workflow: <workflow name or null>
workflow_stage: <short stable stage>
pending_candidates: []
pending_review: <mapping or null>
deferred_items: []
last_completed_action: <mapping or null>
last_canonical_object: <mapping or null>
next_action: <mapping or null>
dirty_index:
  dirty: false
  reason: null
  snapshot_sha256: <index snapshot or null>
stale_reading_notes: []
last_validation_status: <mapping or null>
updated_at: <UTC RFC3339 timestamp>
```

## Reference shapes

`active_source` records `source_id`, registered source version SHA-256, and human title. The current source path is resolved from the Source Registry, not copied into state.

`current_pdf_page` may contain `physical`, `printed`, and the last scanned physical/printed ranges. It does not contain extracted page text.

Each `pending_candidates` item contains only `session`, `candidate_id`, `rating`, `status`, `title`, and `record_path`. The record path is workspace-relative.

`pending_review` contains a session, review path, stage, and object IDs when a concrete review exists. It must be null when no fixed review version is waiting.

`last_completed_action`, `last_canonical_object`, and `next_action` use short summaries and IDs/paths. They must not copy full object bodies or explanations.

`next_action.workflow` identifies the immediate workflow. Ordinary reading, scan continuation and solve actions must not contain `candidate_id`, `review_path`, `knowledge_pack_path`, `pack_id`, `review_object_id` or `review_object_ids`. A `candidate_id` is valid only for Review/Knowledge Pack context and must exactly name a current, unique member of `pending_candidates`. Concrete review/pack/object references require a non-null `pending_review`. Likewise, `pending_review` may be non-null only while Review or Knowledge Pack is active.

`stale_reading_notes` is derived from Reading Note `source_object_id` and `source_revision`. The checkpoint helper refreshes it. A missing source or impossible revision is an integrity issue, not merely stale.

## Checkpoint events

Checkpoint after:

- active Source changes;
- current page or scanned range changes;
- a Candidate is created, adopted, rejected, or deferred;
- a fixed Review is prepared or completed;
- Canonical publish or revision completes;
- a Problem is saved;
- an Insight is approved;
- an Index becomes dirty or is rebuilt;
- validation completes;
- a session ends or hands off.

The helper validates these reference rules during `validate`, `resume` and both sides of `checkpoint`. An invalid merged checkpoint is rejected before any state, previous-state or log write. A valid checkpoint increments `state_revision`, sets `updated_at`, writes through a temporary file plus atomic rename, preserves `CURRENT_STATE.previous.yaml`, and atomically appends a compact entry to `SESSION_LOG.md`.

## Recovery rule

`CURRENT_STATE.yaml` answers “what should happen next.” `SESSION_LOG.md` explains prior milestones. Staging and publication evidence verify the referenced work. If the current file is corrupt, restore `CURRENT_STATE.previous.yaml`, inspect the last Session Log entry and workspace evidence, then create a corrective checkpoint.
