# Adaptive study hub

Use when designing or changing the workspace's course-material homepage. It is a navigation layer over existing files, Reading records and self-test artifacts; it does not create or approve course content.

## Discover before designing

Read the workspace's Reading Library metadata and inspect actual course folders and any self-test archive. Identify course ownership from a verified course code or explicit metadata. Record each navigable file with its type, physical path, display name and available relationship evidence. Recognize lecture slides/notes, tutorials, assignments, labs, formula/reference files, practice questions, returned work, grading/correction and answer keys when they exist; preserve unfamiliar material in an "其他资料" group instead of hiding it. Ignore temporary files and stale build copies. The workspace's `tools/study_hub.py` can produce a deterministic inventory and Staging HTML preview; semantic relationships still require review.

Use the strongest available relation evidence: explicit source ID/version and page span; a self-test's stated source page span; a unique course/lecture label; or an exact file family with a matching question/key role. A shared number alone does **not** prove that Tutorial 4 belongs to Lecture 4. If multiple plausible targets remain, show the files under the course and their own series, without a false same-unit link. Treat a filename hint as a navigation hint, never as authority for source identity or learning correctness.

## Shape the page from the inventory

Start with course selection and search. Within a course, expose only categories that contain real, accessible entries, with the course's own names where useful. Keep published notes easy to open; group original slides with a note only when the relationship is supported. Keep tutorial and assignment series independently reachable when their lecture mapping is unknown. For a self-test, show separate links for the question sheet, submitted work, grading, correction and reference key **only for the stages that actually have files**. Do not infer completion, mastery or a grade from the mere presence of a PDF. Do not expose an internal Staging answer key as a normal published result.

Make common lookup tasks short: choose a course, choose an available material type or search across that course, then open the target. Give a long collection a compact grouped list rather than rendering every file as an undifferentiated scroll. Retain the existing note reader's stars, annotations, paired-slide interaction and authenticated local file access; a homepage redesign must not alter those records or published note bytes.

## Verify and carry forward

Before replacing the live homepage, make a reviewable Staging preview using the current inventory. Check at least one course with self-tests, one without them, and one with a different source-folder vocabulary. Verify every visible link exists, category counts match entries, empty categories are absent, course search spans its categories, and uncertain mappings are not presented as fact. In the live reader, use allowlisted local paths and its existing session protection for raw documents; do not expose arbitrary filesystem paths through URL parameters. Record the discovery rule, ambiguous matches and user's visual feedback. An accepted layout becomes a reader/template change; a Staging sample by itself is not a V1.4 release or proof of future self-test grading features.
