# Resume

Use for “继续”, “继续上次学习”, “resume”, or any fresh Codex session that must recover prior work.

1. Read workspace `AGENTS.md` and this Skill entrypoint.
2. Resolve `scripts/state.py` relative to the loaded Skill directory, then run `<workspace Python> <Skill directory>/scripts/state.py resume --workspace <root>`. Do not look for `tools/state.py` or `scripts/state.py` inside the workspace.
3. Verify the state schema, active Source Registry/version/location, pending record paths, Reading Note revisions and Index state. The helper must reject orphaned Candidate IDs and review references outside Review/Knowledge Pack before reporting the workspace ready.
4. Inspect only referenced Staging/review/publication files. Do not scan all past sessions.
5. If state conflicts with publication or Canonical evidence, trust workspace evidence and prepare a corrective checkpoint.
6. Give the user a concise rendered summary under [User-Facing Delivery](../references/user-delivery.md): source/topic/page, pending candidates/review, last completed action, health issues and next action. Translate machine states into human language and omit raw paths or hashes unless they are necessary to diagnose an error.
7. Continue from `next_action` when safe. A normal reading/solve action has no Candidate or Review reference. Stop at an unresolved Human Review gate; do not reconstruct approval from memory.

If the active PDF is unavailable, Canonical knowledge and Captures remain readable. Report the missing locator and use the rebind workflow rather than guessing a path.
