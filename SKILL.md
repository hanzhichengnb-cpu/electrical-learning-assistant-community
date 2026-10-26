---
name: electrical-learning-assistant-community
description: Operate a compatible local Electrical Engineering Learning System workspace. Use when the user has provided that workspace and wants to resume study, make source-linked reading notes, create or grade courseware-grounded self-tests, organize a course-material homepage, search prior course content, solve an engineering problem, review or save knowledge, or validate the workspace. Requires local workspace access and the workspace's own tools; ordinary standalone electrical engineering questions do not require this skill.
metadata:
  short-description: Study electrical engineering in a compatible local workspace
---

# Electrical Learning Assistant

Treat the workspace as durable memory. Use its files for current page, pending approval, source identity and next action.

## Bootstrap

1. Find the workspace root from its `AGENTS.md`; read that file and `00_System/runtime/CURRENT_STATE.yaml`. Do not assume a machine-specific path.
2. For “继续” or a fresh-session resume, follow [resume](workflows/resume.md) and run this Skill's `scripts/state.py resume` before loading task files.
3. Read the workflow relevant to the request, plus the local workspace specification it names. Use the workspace's existing Python/tools. Local programs must not call the OpenAI API to generate teaching.

## Invariants

- Source, Reading presentation and approved Canonical knowledge have separate authority. Reading pages may be indexed as locators in optional Course Recall, never as approved Canonical knowledge.
- The user approves each concrete Canonical version before publication. A local approval record alone does not grant new authorization; follow [review](workflows/review.md) and [canonicalize](workflows/canonicalize.md).
- Normal scanning, note creation, solving and reflection create no persistent Candidate, Review or pending state. Enter that flow only after the user explicitly asks to save or chooses 保存 or 修改后保存 on a proposed knowledge card.
- Do not invent source facts, user errors or prior decisions. Source-grounded professional English belongs within technical teaching; read [professional English](references/professional-english.md) when studying, reviewing, making notes or solving an English problem.
- Establish understanding before inference. For every new or requested regenerated note, apply [teaching foundations](references/teaching-foundations.md) and the workspace's V1.4 understanding-chain supplement when present: give the learner a real problem entrance, locally rebuild needed prior knowledge, connect symbols to objects and roles, show the skipped reasoning, and close with justified remember/understand/do outcomes. Judge coverage and understandability separately with concrete prose evidence. Supplemental teaching has the same responsibility; prior mention, a glossary, a filled audit or an author-written self-check never proves understanding.

## Optional Course Recall

Use Course Recall alongside Canonical Search only if both `00_System/specs/course-recall-v1.2.md` and `tools/recall.py` exist. Follow that workspace specification and verify original source pages before treating Reading text as fact. Otherwise use the compatible Canonical-only path; never call a missing command.

## Supporting guidance

For written review checklists, self-tests and returned answer sheets, follow [self-test](workflows/self-test.md). Organize related source knowledge around shared diagrams, models or derivation chains, with individually checkable basic subparts and content-appropriate response actions.

For new or requested regenerated source-range notes, follow [source-range authoring](references/conversation-note-authoring.md) and the workspace's active authoring contract. Respect the model and review roles selected by the user or workspace; do not claim a model switch, delegation, or independent review unless the environment actually performed it. Preserve source-linked layout, the official renderer and visual/print acceptance independently of model choice.


For local reading stars, notes and fine annotations, follow [personal annotations](references/personal-annotations.md) and the workspace's active reader contracts. Preserve their independent personal authority and provenance; annotation actions are not knowledge approval or learning progress.

For a course-material homepage or catalogue, follow [adaptive study hub](workflows/study-hub.md). Build its sections from verified files and Reading records actually present in each course; missing categories stay absent, and uncertain cross-file relationships stay unclaimed. Keep this catalogue distinct from the student's progress and Canonical knowledge.

For each source-linked point, identify all visible source content before choosing the locator. Keep the clickable knowledge region separate from the visible outline: place the latter and its number in verified whitespace with room for normal and selected strokes. If a meaningful full frame cannot avoid source ink, use safe partial edge or corner segments while retaining the point number and region click. The renderer checks actual visible marks against protected source regions at supported sizes; visually review the original as the final safeguard. New source-range notes default to verified source-region annotations paired with nearby full teaching when the workspace supplies `source-annotations-v1.3.md`; each complete slide is one unit, with continuous teaching and one original in print (one readable page, or a teaching-only second page). Read the linked `lecture3-compact-acceptance-v1.3.md` before authoring: classify page roles first, keep nontechnical pages to one concise point and one printed page, and require a bound page-specific review for any technical continuation. For this interactive layout, deliver the HTML as the main reading page and the PDF as a labelled static print copy; verify the paired right rail and click/scroll behavior in the browser. The complete left slide must not scroll locally: trackpad scrolling over it moves the outer page, while the right explanation rail scrolls independently. Even a user-facing *preview* must be the official source-annotation render with checked source regions, linked points and a passed interaction build receipt. If the official build or browser check is blocked, retain the draft in Staging and report the blocker; do not substitute a custom slide-plus-paragraph page. This real model/render/validation contract never replaces the v2 dependency and independent teaching review. For a source-range note, follow [reading-note](workflows/reading-note.md); the workspace's current page-study and publication specifications define its data structure and quality gates. Before presenting long or approval-bound content, read [user delivery](references/user-delivery.md). Read [workspace contract](references/workspace-contract.md) for tool and permission boundaries, [state schema](references/state-schema.md) before changing state, and [portability](references/portability.md) for migration or source rebinding.

## Workflow routing

| Intent | Workflow |
|---|---|
| Scan pages, focus mode | [scan](workflows/scan.md) |
| Crop or extract an approved item | [extract](workflows/extract.md) |
| Review candidates or explanations | [review](workflows/review.md) |
| Publish an approved version | [canonicalize](workflows/canonicalize.md) |
| Solve a new problem using prior knowledge | [solve](workflows/solve.md) |
| Perform post-problem reflection | [reflect](workflows/reflect.md) |
| Build or refresh a human reading view or an existing Reading Bundle | [reading-note](workflows/reading-note.md) |
| Organize the course-material homepage across notes, originals, exercises and self-tests | [adaptive study hub](workflows/study-hub.md) |
| Create a courseware-grounded written self-test or grade a returned answer sheet | [self-test](workflows/self-test.md) |
| Resume across sessions | [resume](workflows/resume.md) |
| Validate or diagnose integrity | [validation](workflows/validation.md) |

## Checkpoints

After a durable workflow transition listed in [state schema](references/state-schema.md), run this Skill's `scripts/state.py checkpoint` with a small patch, event and summary. The helper validates references before writing. State stores references and status, never copied teaching or conversation text. A proposed but declined save creates no review checkpoint.

## Maintenance

When the workspace `AGENTS.md` names a maintained Skill copy, edit and validate that copy first, then sync the installed copy and verify that both match. The workspace's `VERSION` tracks the system release; it does not by itself version the Skill.
