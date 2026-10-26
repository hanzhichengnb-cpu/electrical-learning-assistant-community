# Agent workflow

Paths below are examples of roles, not shell fragments to concatenate unsafely. Resolve the package and task paths first; pass paths as proper command arguments. Use the host's own file, image and browser tools.

## Prepare without asking the learner to set up a system

Run:

    python <package>/scripts/notes.py doctor

Use an existing Python interpreter with pypdfium2. Otherwise, when package downloads are allowed:

    python <package>/scripts/bootstrap.py --runtime <task>/.course-notes-runtime

Use the returned interpreter for subsequent commands. This creates an isolated environment and installs one pinned PDF dependency; it does not modify system Python. If the host blocks execution, network installation or local files, report the actual missing capability. Do not ask the learner to create placeholder tools.

Choose a writable library folder, then:

    python <package>/scripts/notes.py prepare --workspace <library> --pdf <uploaded.pdf>

By default all physical pages are selected. Use --pages only for the learner's requested range or an explicitly internal pilot. The command copies the original, creates verified page images and text, initializes the library and returns source.json and lesson.json paths. It never writes teaching.

Open every selected source image with the agent's image/PDF viewer. Infer a short course/title from reliable source evidence and the request. If the course is uncertain, use a neutral title and continue; do not block on naming preferences. Scanned or low-text pages still need visual reading, with OCR through host tools if necessary.

## Author, review, and render

Read format.md and teaching.md. Fill the returned lesson.json with actual point-linked teaching. Keep editable drafts in the returned work folder. Reuse source hashes and physical page IDs; do not change the original or its prepared images.

    python <package>/scripts/notes.py check --workspace <library> --manifest <source.json> --lesson <lesson.json>
    python <package>/scripts/notes.py render --workspace <library> --manifest <source.json> --lesson <lesson.json>

The render creates an internal preview.html and a receipt. The preview banner remains until publication. Reopen the source and perform the separate semantic/geometry pass. Author review.json using the exact current lesson hash returned by check. Repair and re-render after meaningful changes; older hashes cannot approve new content.

## Browser checks

Open preview.html in a real browser. For all pages, inspect source fidelity, unobscured badges/edges, correct source-to-teaching correspondence, readable prose/formulas and complete outcomes. Click every badge and every point's region interior.

Check at desktop widths 1280, 1100 and 1144 (including a short 654px-high window), and a 390px phone width. Desktop: original remains complete, wheel over original moves the outer page, right rail scrolls independently. Phone: source and teaching stack and no content escapes the page. Test source zoom, closing it, theme and directory controls. Print mode must show all teaching and exactly one original image per source page; it need not obey an artificial two-page limit.

The included optional automation uses Node.js and Playwright if the agent already has them:

    node <package>/scripts/check_reader.mjs --html <preview.html> --lesson <lesson.json> --output <browser-review.json> --screenshots <qa-directory>

It also accepts --playwright <module-path> and --chromium <browser-executable>. It launches a disposable browser profile. It does not read the user's browser cookies. Do not install a full browser if the host already provides suitable native browser inspection.

Automation records behavior and produces screenshots; visual_review stays pending. Inspect the actual images before setting that dimension to passed with specific evidence and the inspected physical pages. The source-overlay marks especially require visual judgment.

With native browser tools, perform the same checks and write browser-review.json in the documented format using the actual preview and lesson hashes. If a check cannot be performed, retain its unpassed state. Never mark everything passed merely to satisfy the publisher.

## Publish and deliver

    python <package>/scripts/notes.py publish --workspace <library> --manifest <source.json> --lesson <lesson.json> --review <review.json> --qa <browser-review.json>

Publication validates source/image hashes, lesson structure and exact current review bindings. It writes a versioned self-contained HTML, retains the editable lesson and review records, updates the searchable library homepage and creates desktop launch helpers. Prior note versions remain immutable and linked from the homepage. A partial/unpassed draft stays in .work and does not replace the current note.

Open the returned homepage or note with the host's file/browser capability. The simplest portable entry is index.html; generated Mac .command and Windows .cmd helpers are conveniences and may still be subject to operating-system security prompts. Do not promise to bypass those prompts. No server is required to read the HTML. A sandboxed/cloud host may need to attach the HTML as a downloadable artifact instead of opening a local browser tab.

Give the primary reading link and one short sentence about what range is complete. Offer the library ZIP when the host's local filesystem is temporary. Tell the learner only a real limitation that affects their result, not internal schema/receipt details.

For a revision, edit a work copy, review, render, check and publish again. Never edit an already published version directory in place. For another PDF, repeat prepare in the same library; organization and homepage updates happen automatically. The agent's current conversation model supplies all teaching, with no model routing or external model API.
