# Review

Use when the user explicitly asks to save knowledge, chooses 保存/修改后保存 on a knowledge card already shown in the conversation, or must approve a concrete image, explanation, object or revision. Ordinary Scan, Reading Note, Solve and Reflect work does not enter persistent Review before that choice.

1. Resume the exact session and inspect Staging status. Publication receipts override stale local review labels.
2. Build the exact submission under [User-Facing Delivery](../references/user-delivery.md) and [Integrated Professional English](../references/professional-english.md). Prefer one coherent Knowledge Pack when the workspace supports it: show what it is, why it is worth saving, source course/pages, core conclusion or formula, conditions, problem triggers, main connections and uncertainty. A pack may bind several exact backend drafts, but approval applies only to the concrete versions shown. For legacy workspaces, use the existing exact-version review artifact. Do not submit a `.md` file or make the user inspect hashes or paths.
3. Apply requested edits only in Staging. A material content change invalidates approval of the earlier version; regenerate and resubmit the full rendered artifact before requesting another decision.
   Before marking a teaching explanation ready, apply [Teaching Foundations](../references/teaching-foundations.md). Separate factual/content coverage from reader understanding; record specific passages showing concept establishment, condition reasons and key steps. A knowledge approval decision is separate from this teaching audit.
4. Build the workspace’s `review.json` with hashes and target IDs after the content is fixed. Mark user decisions only from actual conversation authorization.
5. End the batch with a deduplicated professional-English review in knowledge order and, when useful, a small active-recall set with its answer key under a distinct heading or styled block. Keep sourced slide wording distinct from Codex supplemental usage notes.
6. The first retention choice belongs to Solve or Reflect and uses exactly 保存、修改后保存、暂不保存、不再建议. After that choice starts Review, checkpoint `pending_review` only when a concrete version has been shown and awaits its separate publication decision; set `next_action` to that exact Review/Pack action. A non-save choice leaves no new Candidate or pending state.

Review completion means a concrete version is ready for approval. It does not itself authorize Canonical publication.
