# User-Facing Delivery

Use this reference whenever workspace content will be submitted for the user to read, check, compare, or approve. It governs presentation only and does not change the authority of Canonical Markdown/YAML or any approval boundary.

## Required delivery form

- Keep Markdown, YAML, JSON, hashes, file paths, state fields, and manifests as internal storage and machine evidence.
- Never ask the user to open or approve a `.md` file, raw Markdown, JSON, YAML, or a filesystem path. Do not cite or link internal skill/workflow files as execution evidence in learning, review, or approval material; report compliance in plain language.
- For short material, present the complete content directly in the rendered conversation with readable headings, prose, formulas, images, and lists.
- For source-region annotated study notes (`source-annotations-v1`), deliver the interactive HTML reading page as the primary, directly openable artifact. It has the complete slide on the left and linked explanations on the right. Scrolling over the left slide moves the whole page between slides; the left slide never scrolls locally. The right explanation rail scrolls independently, and clicking a source number locates its matching explanation. Supply the PDF only as a clearly labelled static print/export companion; its printed columns cannot provide click or internal scrolling. Do not present or link the PDF alone as the reading result.
- Apply that rule to previews as well as finished notes. Link only the official renderer's HTML with a matching passed interaction receipt; a custom side-by-side page without source boxes, numbered links and checked scrolling is not a preview of this reading mode. If verification is unavailable, explain the blocker without handing over that substitute page.
- For other long, multi-page, image-heavy, or durable material, generate a fully typeset PDF as the primary deliverable. An immediately readable HTML page may be supplied as a preview or accessibility alternative.
- Deliver the rendered artifact as an openable attachment or file. Do not make the user navigate internal directories.

## Mathematics and technical notation

- Render every mathematical expression. Inline and display math may be authored internally with `$...$`, `$$...$$`, or equivalent structured input, but the user must see typeset mathematics rather than delimiters or LaTeX source.
- Use aligned display layout for multi-step derivations. Keep equality alignment, law or step labels, and surrounding Chinese explanation readable.
- Do not use code spans or code blocks for formulas, variables, units, matrices, derivatives, or transfer functions.
- Before delivery, check for visible raw tokens such as `$$`, `\\begin{...}`, `\\text{...}`, or unexpanded commands, and verify that formulas are not clipped or split awkwardly across pages.

## Source evidence and images

- Embed source images, circuit diagrams, plots, and page screenshots beside the explanation or candidate they support. Use human captions with physical page and verified printed page; write “未核实” when the printed page is unknown.
- Do not expose an image path in place of the image. Preserve aspect ratio, legibility, and the relationship between evidence and interpretation.
- Clearly distinguish source content, Codex explanation, and proposed Canonical content. Never use visual polish to blur provenance or uncertainty.
- Render English phrases as normal prose or italics, never as program code. Keep English terms, Chinese meanings, formulas, figures, and source pages visually connected.

## Candidate and approval presentation

Convert internal candidate queues into readable approval cards or a concise rendered checklist. For each candidate, show the candidate ID, title, rating when used, source pages, source evidence, core content and formulas, retention value, conditions or limitations, duplicate status in human language, proposed object action/type, and the exact decision requested.

Keep technical review records internal. Hide hashes, UUIDs, capture IDs, manifest paths, schema versions, raw relations, and machine status fields unless a specific error cannot be understood without one of them.

Approval binds only the complete rendered version shown to the user. After any change to content, evidence, formulas, conditions, proposed relations, or the decision requested, regenerate and resubmit the full artifact. A partial change summary may accompany it but cannot replace the updated artifact.

## Boundary and verification

Rendering, exporting, or opening an artifact does not mean the user approved its content. Candidate selection, crop approval, explanation approval, object-version approval, and Canonical publication remain separate decisions exactly as defined by the existing workflows.

Before delivery, verify:

1. The artifact opens and is readable in its intended viewer.
2. Mathematics is fully rendered and unclipped.
3. Images are embedded near their evidence and have human captions.
4. Major claims and candidates trace to specific pages, with unknown page labels marked rather than guessed.
5. Internal machine fields are absent from visible prose unless diagnostically necessary.
6. The complete current version and exact pending decisions are present.
7. No rendering or formatting step has been recorded as user approval or Canonical authorization.

Use the workspace’s approved renderer and templates when available. If a workspace lacks a suitable presentation template, the Skill’s `assets/user-delivery/standard-v1/` provides a neutral HTML/PDF starting point; adapt presentation without changing knowledge meaning.
