# Canonicalize

Use only when the user approves the exact displayed Review version.

1. Resume and verify the review hash, files, source checks, object targets and approval scope. If the exact version must be shown again, use the complete rendered artifact required by [User-Facing Delivery](../references/user-delivery.md), never the internal Markdown or review metadata.
2. Record the real approval in the workspace’s expected approval format. Do not infer authorization from an editable local file.
3. Publish through the workspace CLI. For revision, preserve ID and use the exact base revision/hash; let the tool archive history.
4. Read back each target and validate the published object.
5. Rebuild or incrementally update the Index using the existing workspace capability, then verify Search/readback.
6. Checkpoint the Candidate decision, last Canonical object, clean/dirty Index state, validation state and next action. Append a concise Session Log entry.

Keep the sequence `Publish → Validate object → Update Index → Validate Index`. A failure after Publish does not justify deleting the committed object.
