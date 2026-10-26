# Lesson and review formats

All JSON is UTF-8. These are authoring files for the agent, not a user-facing interface. Scripts never invent teaching or generate an automatic semantic pass.

## lesson.json

prepare returns an unfilled scaffold. Keep schema=1, source_sha256 and exactly the selected physical page numbers. Set a verified course/title and author every page.

    {
      "schema": 1,
      "source_sha256": "<exact value from source.json>",
      "title": "A meaningful lesson title",
      "course": "Course name, or an empty string",
      "pages": [{
        "page": 1,
        "kind": "technical",
        "title": "What this page teaches",
        "lead": "The actual problem and entrance to this page.",
        "points": [{
          "id": "p0001-k01",
          "title": "A source-grounded teaching point",
          "region": [0.1, 0.2, 0.5, 0.3],
          "outline": [0.09, 0.19, 0.52, 0.32],
          "edges": ["top", "left", "bottom"],
          "badge": [0.08, 0.20],
          "blocks": [
            {"type": "paragraph", "text": "Explain the source objects and reasoning."},
            {"type": "equation", "tex": "Y(s)=G(s)U(s)"},
            {"type": "list", "ordered": false, "items": ["A justified observation"]},
            {"type": "callout", "label": "Supplement", "text": "Label additions honestly."}
          ]
        }],
        "outcomes": {
          "remember": ["A source-justified conclusion, with its condition"],
          "understand": ["A relationship or reason"],
          "do": ["An observable reasoning or application action"]
        }
      }]
    }

Page kinds: technical, cover, agenda, divider, repeat, blank. Technical pages require justified outcomes. Nontechnical pages still retain their original image and a concise explanation of their role; do not fill a cover with invented technical teaching.

Each region is normalized [x,y,width,height] from the image's top-left. It defines the click target; outline separately defines the visible locator. Omit outline to use the click rectangle. edges may be a subset, or [] for a badge without any drawn frame. Use this where a safe rectangle would cross source ink. badge is an optional normalized [x,y]; explicitly place it in real whitespace when needed.

Point IDs use physical source page numbers, such as p0024-k03. Keep IDs stable when revising the same concept. Points on one page are local counterparts of the source objects, not arbitrary paragraph counts. Check overlaps visually; the reader selects the smallest matching region when source targets overlap.

Blocks support paragraph, equation, list, table, callout and quote. quote text is marked as original-source quotation. For table use columns:[string,...] and rows:[[string,...],...]. Plain text is escaped, so do not write raw HTML or Markdown headings/emphasis and expect it to execute. Use separate blocks instead. Text paragraphs/cells may contain inline LaTeX using \( ... \); in JSON backslashes must be doubled, for example "\\(RCs+1\\)". An equation block's tex contains the LaTeX only, with no surrounding delimiters. Do not insert network-loading or active-link TeX macros.

Split multiple relations or derivation stages into separate equation blocks when needed for readable mobile display; use aligned LaTeX for meaningful multi-line derivations. Do not leave an important formula clipped off the right edge or shrink it into unreadable type.

## review.json

After drafting, reopen the source and do a separate review. Use the actual lesson_sha256 returned by check. All selected pages appear in source order.

    {
      "schema": 1,
      "method": "separate-source-to-body-pass",
      "source_sha256": "<source hash>",
      "lesson_sha256": "<hash of exact lesson.json bytes>",
      "pages": [{
        "page": 1,
        "source_evidence": "Specific source equation, figure, conditions, or page role.",
        "coverage": {"status": "passed", "evidence": "Concrete source-to-body correspondence."},
        "teaching": {"status": "passed", "evidence": "Actual passages establishing meanings and steps."},
        "geometry": {"status": "passed", "evidence": "Specific inspected source objects, outlines and badges."}
      }]
    }

Any failed dimension stays failed until repaired. Do not fill evidence with vague “all complete” assertions. Structural validation cannot verify whether these semantic judgments are true.

## browser-review.json

Automated browser checks can author the measured part. The agent still inspects the actual source/teaching screenshots for every page and fills visual_review truthfully. With native browser tools it can author the complete record from observed behavior:

    {
      "schema": 1,
      "status": "passed",
      "lesson_sha256": "<exact lesson hash>",
      "html_sha256": "<exact preview.html byte hash>",
      "inspected_pages": [1],
      "checks": {
        "source_visible": true,
        "point_links": true,
        "rail_scroll": true,
        "outer_scroll": true,
        "math_readable": true,
        "responsive_layout": true,
        "no_external_requests": true
      },
      "evidence": "Specific browser, tested sizes, point actions and observed results.",
      "visual_review": {
        "status": "passed",
        "inspected_pages": [1],
        "evidence": "Specific rendered source/teaching inspections, including repaired defects."
      }
    }

The review records refer to the internal preview; publication removes only its draft banner. Renderer/assets changing after inspection requires another render and browser review. The published HTML embeds all page images, styles, reader code and the vendored SVG math engine, so moving that HTML alone does not break its reading content.
