#!/usr/bin/env python3
"""Portable course-note mechanics. Teaching is authored by the active AI agent."""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import struct
import sys
import tempfile
import zlib

PACKAGE = Path(__file__).resolve().parent.parent


class NoteError(Exception):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def write_atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        data = data.encode()
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as out:
        out.write(data)
        temp = Path(out.name)
    os.replace(temp, path)


def require(condition, message):
    if not condition:
        raise NoteError(message)


def under(root, relative):
    root = Path(root).resolve()
    target = (root / relative).resolve()
    require(target.is_relative_to(root), "A package path escapes its workspace.")
    return target


def init(root):
    root = Path(root).resolve()
    for name in ["sources", ".work", "lessons"]:
        (root / name).mkdir(parents=True, exist_ok=True)
    if not (root / "library.json").exists():
        write_atomic(root / "library.json", encoded({"schema": 1, "lessons": []}))
    refresh_library(root)
    return root


def select_pages(raw, count):
    if raw is None:
        return list(range(1, count + 1))
    selected = set()
    for part in raw.split(","):
        span = part.strip().split("-")
        require(len(span) in (1, 2) and all(v.isdigit() for v in span),
                "Use physical page numbers such as 1-8,10.")
        start, end = int(span[0]), int(span[-1])
        require(1 <= start <= end <= count, "Requested pages are outside the PDF.")
        selected.update(range(start, end + 1))
    require(selected, "Select at least one page.")
    return sorted(selected)


def pdf_runtime():
    try:
        import pypdfium2 as pdfium
        return pdfium
    except ImportError as exc:
        raise NoteError("PDF support is unavailable. The agent should run scripts/bootstrap.py "
                        "in an isolated runtime, then retry with that Python interpreter.") from exc


def png_bytes(bitmap):
    """Encode the explicitly RGB PDFium bitmap with the Python standard library."""
    require(bitmap.n_channels == 3, "PDF renderer did not produce an RGB bitmap.")
    pixels = bytes(bitmap.buffer)
    rows = b"".join(b"\0" + pixels[y * bitmap.stride:y * bitmap.stride + bitmap.width * 3]
                    for y in range(bitmap.height))
    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data +
                struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff))
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", bitmap.width, bitmap.height, 8, 2, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(rows, 6)) + chunk(b"IEND", b""))


def prepare(args):
    pdfium = pdf_runtime()
    root = init(args.workspace)
    source = Path(args.pdf).resolve()
    require(source.is_file() and source.suffix.lower() == ".pdf", "Provide an existing PDF.")
    data = source.read_bytes()
    source_hash = digest(data)
    source_id = source_hash[:20]
    destination = root / "sources" / (source_id + ".pdf")
    if destination.exists():
        require(digest(destination.read_bytes()) == source_hash, "Stored source hash mismatch.")
    else:
        write_atomic(destination, data)
    try:
        document = pdfium.PdfDocument(str(destination))
    except Exception as exc:
        raise NoteError("The PDF could not be opened. Check corruption or password protection.") from exc
    try:
        pages = select_pages(args.pages, len(document))
        work = root / ".work" / source_id / ("pages-" + digest(encoded(pages))[:12])
        work.mkdir(parents=True, exist_ok=True)
        records = []
        for number in pages:
            page = document[number - 1]
            textpage = page.get_textpage()
            try:
                text = textpage.get_text_bounded()
            finally:
                textpage.close()
            width, height = page.get_size()
            picture = work / ("page-%04d.png" % number)
            bitmap = page.render(scale=min(2.0, 1600 / width), rev_byteorder=True,
                                 force_bitmap_format=pdfium.raw.FPDFBitmap_BGR)
            try:
                write_atomic(picture, png_bytes(bitmap))
            finally:
                bitmap.close()
            page.close()
            textfile = work / ("page-%04d.txt" % number)
            write_atomic(textfile, text)
            records.append({"page": number, "width": width, "height": height,
                            "image": str(picture.relative_to(root)),
                            "image_mime": "image/png",
                            "image_sha256": digest(picture.read_bytes()),
                            "text": str(textfile.relative_to(root)),
                            "needs_visual_reading": len(text.strip()) < 40})
        manifest = {"schema": 1, "source_id": source_id, "source_sha256": source_hash,
                    "source": str(destination.relative_to(root)), "source_name": source.name,
                    "total_pages": len(document), "selected_pages": pages, "pages": records}
        write_atomic(work / "source.json", encoded(manifest))
        scaffold = work / "lesson.json"
        if not scaffold.exists():
            write_atomic(scaffold, encoded({
                "schema": 1, "source_sha256": source_hash, "title": source.stem,
                "course": "", "pages": [
                    {"page": n, "kind": "technical", "title": "", "lead": "",
                     "points": [], "outcomes": {"remember": [], "understand": [], "do": []}}
                    for n in pages]}))
        return {"workspace": str(root), "source_manifest": str(work / "source.json"),
                "lesson": str(scaffold), "pages_to_inspect": len(pages),
                "next": "Inspect every selected page image, then author lesson.json. "
                        "The scaffold contains no teaching."}
    finally:
        document.close()


def valid_text(value, label):
    require(isinstance(value, str) and value.strip(), label + " must contain actual content.")
    require(not re.search(r"\\(?:href|url|require|includegraphics|htmlStyle|htmlClass)\s*[{[]", value),
            label + " contains unsupported active TeX commands.")


def rect(value, label):
    require(isinstance(value, list) and len(value) == 4 and
            all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in value),
            label + " must be normalized [x, y, width, height].")
    x, y, w, h = value
    require(0 <= x < 1 and 0 <= y < 1 and w > 0 and h > 0 and
            x + w <= 1.000001 and y + h <= 1.000001, label + " is outside its source image.")


def validate_block(block):
    require(isinstance(block, dict), "A teaching block must be an object.")
    kind = block.get("type")
    require(kind in ("paragraph", "equation", "list", "table", "callout", "quote"),
            "Unknown teaching block type.")
    if kind == "equation":
        valid_text(block.get("tex"), "Equation")
    elif kind == "list":
        require(isinstance(block.get("items"), list) and block["items"], "List needs items.")
        for item in block["items"]:
            valid_text(item, "List item")
    elif kind == "table":
        columns, rows = block.get("columns"), block.get("rows")
        require(isinstance(columns, list) and columns and isinstance(rows, list) and rows,
                "Table requires columns and rows.")
        require(all(isinstance(v, str) for v in columns), "Table headers must be strings.")
        require(all(isinstance(r, list) and len(r) == len(columns) and
                    all(isinstance(v, str) for v in r) for r in rows), "Invalid table cells.")
    else:
        valid_text(block.get("text"), "Teaching paragraph")


def load_lesson(root, manifest_path, lesson_path):
    root = Path(root).resolve()
    manifest, lesson = read_json(manifest_path), read_json(lesson_path)
    require(manifest.get("schema") == lesson.get("schema") == 1, "Unsupported schema.")
    require(lesson.get("source_sha256") == manifest["source_sha256"],
            "The lesson belongs to a different PDF.")
    require(digest(under(root, manifest["source"]).read_bytes()) == manifest["source_sha256"],
            "Original PDF has changed.")
    valid_text(lesson.get("title"), "Lesson title")
    require(isinstance(lesson.get("course"), str), "Course must be a string.")
    pages = lesson.get("pages")
    require(isinstance(pages, list) and
            [p.get("page") for p in pages] == manifest["selected_pages"],
            "Lesson must cover exactly the requested physical pages in order.")
    ids = set()
    for page, source in zip(pages, manifest["pages"]):
        require(page.get("kind") in ("technical", "cover", "agenda", "divider", "repeat", "blank"),
                "Choose each page kind from the actual source.")
        valid_text(page.get("title"), "Page title")
        valid_text(page.get("lead"), "Page entrance or orientation")
        points = page.get("points")
        require(isinstance(points, list) and points, "Every page needs an authored point.")
        for point in points:
            identity = point.get("id")
            require(isinstance(identity, str) and re.fullmatch(r"p\d{4}-k\d{2,}", identity)
                    and identity not in ids and
                    identity.startswith("p%04d-" % page["page"]), "Invalid or duplicate point ID.")
            ids.add(identity)
            valid_text(point.get("title"), "Point title")
            rect(point.get("region"), "Source click region")
            if point.get("outline") is not None:
                rect(point["outline"], "Visible source outline")
            if point.get("badge") is not None:
                require(isinstance(point["badge"], list) and len(point["badge"]) == 2 and
                        all(isinstance(v, (int, float)) and 0 <= v <= 1
                            for v in point["badge"]), "Badge must be normalized [x,y].")
            if point.get("edges") is not None:
                require(isinstance(point["edges"], list) and
                        all(v in ("top", "right", "bottom", "left") for v in point["edges"]),
                        "Visible edges must be top/right/bottom/left.")
            blocks = point.get("blocks")
            require(isinstance(blocks, list) and blocks, "Every point needs real teaching.")
            for block in blocks:
                validate_block(block)
        outcomes = page.get("outcomes", {})
        require(all(isinstance(outcomes.get(k), list) and
                    all(isinstance(v, str) and v.strip() for v in outcomes[k])
                    for k in ("remember", "understand", "do")), "Invalid page outcomes.")
        if page["kind"] == "technical":
            require(any(outcomes.values()), "Technical pages need justified learning outcomes.")
        picture = under(root, source["image"])
        require(digest(picture.read_bytes()) == source["image_sha256"],
                "Prepared source image changed. Re-run source preparation.")
    return manifest, lesson


def esc(value):
    return html.escape(str(value), quote=True)


def prose(value):
    return esc(value).replace("\n", "<br>")


def render_block(block):
    kind = block["type"]
    if kind == "equation":
        return '<div class="equation">\\[' + esc(block["tex"]) + '\\]</div>'
    if kind == "list":
        tag = "ol" if block.get("ordered") else "ul"
        return "<" + tag + ">" + "".join("<li>" + prose(v) + "</li>"
                                          for v in block["items"]) + "</" + tag + ">"
    if kind == "table":
        return '<div class="table-wrap"><table><thead><tr>' + "".join(
            "<th>" + prose(c) + "</th>" for c in block["columns"]
        ) + "</tr></thead><tbody>" + "".join(
            "<tr>" + "".join("<td>" + prose(c) + "</td>" for c in row) + "</tr>"
            for row in block["rows"]) + "</tbody></table></div>"
    if kind == "callout":
        return '<aside class="callout"><b>' + esc(block.get("label", "补充理解")) + \
               "</b><p>" + prose(block["text"]) + "</p></aside>"
    if kind == "quote":
        return '<blockquote><small>原文摘录</small>' + prose(block["text"]) + "</blockquote>"
    return "<p>" + prose(block["text"]) + "</p>"


def source_controls(page):
    buttons, outlines = [], []
    for index, point in enumerate(page["points"], 1):
        x, y, w, h = point["region"]
        buttons.append('<button class="source-hit" data-point="' + point["id"] +
                       '" aria-label="' + esc(str(index) + " · " + point["title"]) +
                       '" style="left:%.5f%%;top:%.5f%%;width:%.5f%%;height:%.5f%%"'
                       ' data-area="%.8f"></button>' % (x * 100, y * 100, w * 100, h * 100, w * h))
        ox, oy, ow, oh = point.get("outline") or point["region"]
        edges = point.get("edges", ["top", "right", "bottom", "left"])
        border = ";".join("border-" + e + ":1.5px solid currentColor" for e in edges)
        outlines.append('<span class="source-outline" data-for="' + point["id"] +
                        '" style="left:%.5f%%;top:%.5f%%;width:%.5f%%;height:%.5f%%;%s"></span>'
                        % (ox * 100, oy * 100, ow * 100, oh * 100, border))
        bx, by = point.get("badge") or [max(.018, min(.98, ox)), max(.025, min(.975, oy))]
        buttons.append('<button class="source-badge" data-point="' + point["id"] +
                       '" aria-label="' + esc("定位知识点 " + str(index)) +
                       '" style="left:%.5f%%;top:%.5f%%">%d</button>' % (bx * 100, by * 100, index))
    return "".join(outlines + buttons)


def render_html(root, manifest, lesson, lesson_hash, draft=True):
    navigation, units = [], []
    for page, source in zip(lesson["pages"], manifest["pages"]):
        number = page["page"]
        navigation.append('<a href="#page-%d"><span>%02d</span>%s</a>'
                          % (number, number, esc(page["title"])))
        image = base64.b64encode(under(root, source["image"]).read_bytes()).decode()
        teaching = []
        for index, point in enumerate(page["points"], 1):
            teaching.append('<article class="point" id="' + point["id"] + '" tabindex="-1">'
                            '<h3><button class="point-number" data-point="' + point["id"] +
                            '">' + str(index) + '</button>' + esc(point["title"]) + "</h3>" +
                            "".join(render_block(b) for b in point["blocks"]) + "</article>")
        outcomes = "".join("<div><h4>" + label + "</h4><ul>" +
                           "".join("<li>" + prose(v) + "</li>" for v in page["outcomes"][key]) +
                           "</ul></div>" for key, label in
                           [("remember", "记住"), ("understand", "理解"), ("do", "会做")]
                           if page["outcomes"][key])
        units.append('<section class="slide-unit" id="page-%d" data-page="%d">'
                     '<div class="unit-heading"><div><span class="eyebrow">课件第 %d 页</span>'
                     '<h2>%s</h2></div><span class="point-count">%d 个讲解点</span></div>'
                     '<div class="paired"><div class="source-column"><div class="source-tools">'
                     '<span>原课件 · 点编号或框内查看讲解</span>'
                     '<button class="zoom-source" data-page="%d">放大原页</button></div>'
                     '<div class="source-canvas"><img src="data:%s;base64,%s" '
                     'alt="原课件第 %d 页" width="%s" height="%s">%s</div></div>'
                     '<div class="teaching-rail" tabindex="0" aria-label="第 %d 页讲解">'
                     '<p class="page-lead">%s</p>%s<div class="outcomes">%s</div>'
                     '</div></div></section>' %
                     (number, number, number, esc(page["title"]), len(page["points"]), number,
                      source.get("image_mime", "image/jpeg"), image, number,
                      source["width"], source["height"], source_controls(page),
                      number, prose(page["lead"]), "".join(teaching), outcomes))
        if not outcomes:
            units[-1] = units[-1].replace('<div class="outcomes"></div>', "")
    css = (PACKAGE / "assets/reader.css").read_text()
    script = (PACKAGE / "assets/reader.js").read_text().replace("</script", "<\\/script")
    math = (PACKAGE / "assets/vendor/mathjax-tex-svg.js").read_text().replace("</script", "<\\/script")
    config = r"""window.MathJax={loader:{load:[]},tex:{inlineMath:[['\\(','\\)']],displayMath:[['\\[','\\]']]},svg:{fontCache:'local'},options:{enableMenu:false}};"""
    banner = '<div class="draft-banner">预览 · 内容与页面效果仍需复核</div>' if draft else ""
    document = ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; '
                'script-src \'unsafe-inline\'; style-src \'unsafe-inline\'; img-src data:; '
                'font-src data:; connect-src \'none\'; base-uri \'none\'; form-action \'none\'">'
                '<meta name="referrer" content="no-referrer"><title>' + esc(lesson["title"]) +
                '</title><style>' + css + '</style><script>' + config + '</script><script>' +
                math + '</script></head><body>' + banner +
                '<header class="topbar"><a class="brand" href="../../../index.html">'
                '<span class="brand-mark">N</span>课件笔记</a>'
                '<div class="header-actions"><button id="toggle-navigation">目录</button>'
                '<button id="toggle-theme">深色</button><button id="print-note">打印</button></div></header>'
                '<div class="reader-layout"><nav class="page-navigation" aria-label="页面目录">'
                '<p class="eyebrow">CONTENTS</p><h2>本讲目录</h2>' + "".join(navigation) +
                '</nav><main><section class="lesson-intro"><p class="eyebrow">' +
                esc(lesson["course"] or "我的课程") + '</p><h1>' + esc(lesson["title"]) +
                '</h1><p>原课件与讲解放在一起。点击编号定位，按自己的节奏读懂。</p>'
                '<div class="lesson-meta"><span>' + str(len(lesson["pages"])) +
                ' 页课件</span><span>' + str(sum(len(p["points"]) for p in lesson["pages"])) +
                ' 个讲解点</span><span>支持离线阅读</span></div></section>' +
                "".join(units) + '<footer>依据你提供的课件整理 · 原页码可追溯 · ' +
                esc(lesson["title"]) + '</footer></main></div>'
                '<dialog id="source-zoom"><button id="close-zoom" aria-label="关闭原页放大">关闭</button>'
                '<img alt="放大的原课件"></dialog><script>' + script + '</script></body></html>')
    return document.encode()


def render(args):
    root = init(args.workspace)
    manifest, lesson = load_lesson(root, args.manifest, args.lesson)
    lesson_data = Path(args.lesson).read_bytes()
    body = render_html(root, manifest, lesson, digest(lesson_data))
    destination = Path(args.lesson).resolve().parent / "preview.html"
    write_atomic(destination, body)
    receipt = {"schema": 1, "source_sha256": manifest["source_sha256"],
               "lesson_sha256": digest(lesson_data), "html_sha256": digest(body),
               "preview": str(destination), "pages": len(lesson["pages"]),
               "points": sum(len(p["points"]) for p in lesson["pages"])}
    write_atomic(destination.with_suffix(".receipt.json"), encoded(receipt))
    return receipt


def check_review(manifest, lesson, review, lesson_hash):
    require(review.get("schema") == 1 and
            review.get("source_sha256") == manifest["source_sha256"] and
            review.get("lesson_sha256") == lesson_hash, "Teaching review is missing or stale.")
    require(review.get("method") == "separate-source-to-body-pass",
            "Reopen the source and perform a separate exact-body review.")
    pages = review.get("pages")
    require(isinstance(pages, list) and
            [p.get("page") for p in pages] == manifest["selected_pages"],
            "Review must cover every requested physical page.")
    for record in pages:
        valid_text(record.get("source_evidence"), "Source evidence")
        for dimension in ("coverage", "teaching", "geometry"):
            result = record.get(dimension, {})
            require(result.get("status") == "passed", dimension + " review has not passed.")
            valid_text(result.get("evidence"), dimension + " evidence")


def publish(args):
    root = init(args.workspace)
    manifest, lesson = load_lesson(root, args.manifest, args.lesson)
    lesson_data = Path(args.lesson).read_bytes()
    lesson_hash = digest(lesson_data)
    review, qa = read_json(args.review), read_json(args.qa)
    check_review(manifest, lesson, review, lesson_hash)
    preview = Path(args.lesson).resolve().parent / "preview.html"
    require(preview.exists(), "Render a preview before publication.")
    require(qa.get("schema") == 1 and qa.get("lesson_sha256") == lesson_hash and
            qa.get("html_sha256") == digest(preview.read_bytes()), "Browser review is missing or stale.")
    require(qa.get("status") == "passed" and
            qa.get("inspected_pages") == manifest["selected_pages"],
            "Inspect every page before publishing.")
    for check in ("source_visible", "point_links", "rail_scroll", "outer_scroll",
                  "math_readable", "responsive_layout", "no_external_requests"):
        require(qa.get("checks", {}).get(check) is True, "Browser check missing: " + check)
    valid_text(qa.get("evidence"), "Browser review evidence")
    visual = qa.get("visual_review", {})
    require(visual.get("status") == "passed" and
            visual.get("inspected_pages") == manifest["selected_pages"],
            "Automated checks do not replace inspection of every rendered source and lesson.")
    valid_text(visual.get("evidence"), "Visual review evidence")
    body = render_html(root, manifest, lesson, lesson_hash, draft=False)
    # Publication changes only the draft banner and the page's storage location.
    preview_expected = render_html(root, manifest, lesson, lesson_hash, draft=True)
    require(preview.read_bytes() == preview_expected, "Preview differs from current renderer/assets.")
    version = digest(lesson_data + encoded(review) + encoded(qa) + body)[:20]
    source_id = manifest["source_id"]
    relative = Path("lessons") / source_id / version
    destination = root / relative
    if destination.exists():
        require((destination / "index.html").read_bytes() == body,
                "A stored version is immutable.")
    else:
        temp = Path(tempfile.mkdtemp(prefix=".publish-", dir=root / "lessons"))
        try:
            (temp / "index.html").write_bytes(body)
            (temp / "lesson.json").write_bytes(lesson_data)
            (temp / "review.json").write_bytes(encoded(review))
            (temp / "browser-review.json").write_bytes(encoded(qa))
            (temp / "source.json").write_bytes(encoded(manifest))
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(temp, destination)
        finally:
            if temp.exists():
                shutil.rmtree(temp)
    library = read_json(root / "library.json")
    existing = next((v for v in library["lessons"] if
                     v["source_id"] == source_id and v["selected_pages"] == manifest["selected_pages"]), None)
    entry = {"source_id": source_id, "source_sha256": manifest["source_sha256"],
             "selected_pages": manifest["selected_pages"], "title": lesson["title"],
             "course": lesson["course"], "version": version,
             "path": str(relative / "index.html"), "history": [],
             "updated_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    if existing:
        entry["history"] = existing.get("history", [])
        if existing["version"] != version:
            entry["history"].insert(0, {k: existing[k] for k in ("version", "path", "updated_at")})
        library["lessons"].remove(existing)
    library["lessons"].append(entry)
    write_atomic(root / "library.json", encoded(library))
    refresh_library(root)
    return {"workspace": str(root), "homepage": str(root / "index.html"),
            "note": str(destination / "index.html"), "version": version,
            "source_unchanged": True}


def natural(value):
    return [int(v) if v.isdigit() else v.casefold() for v in re.split(r"(\d+)", value)]


def refresh_library(root):
    library = read_json(root / "library.json")
    entries = sorted(library["lessons"], key=lambda v: (
        natural(v["course"]), natural(v["title"]), v["selected_pages"][0]))
    cards = []
    for item in entries:
        course = item["course"] or "我的课程"
        page_label = str(item["selected_pages"][0]) + "–" + str(item["selected_pages"][-1])
        history = ""
        if item.get("history"):
            history = '<details><summary>过往版本</summary>' + "".join(
                '<a href="' + esc(v["path"]) + '">' + esc(v["updated_at"][:10]) +
                " · " + esc(v["version"][:7]) + "</a>" for v in item["history"]) + "</details>"
        cards.append('<article class="library-card" data-search="' +
                     esc(course + " " + item["title"]) + '"><p class="eyebrow">' + esc(course) +
                     '</p><h2><a href="' + esc(item["path"]) + '">' + esc(item["title"]) +
                     '</a></h2><p>原课件第 ' + page_label + ' 页 · 可离线阅读</p><a class="read-link" href="' +
                     esc(item["path"]) + '">打开笔记 <span>↗</span></a>' + history + "</article>")
    content = "".join(cards) or '<div class="empty-library">把课件发给你的 AI，它会把笔记整理在这里。</div>'
    css = (PACKAGE / "assets/reader.css").read_text()
    page = ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>我的课件笔记</title><style>' + css + '</style></head><body>'
            '<header class="topbar"><span class="brand"><span class="brand-mark">N</span>课件笔记</span>'
            '<span class="library-caption">你的课程，慢慢读懂。</span></header><main class="library-main">'
            '<p class="eyebrow">YOUR STUDY SPACE</p><h1>打开课件，<br>把理解留在这里。</h1>'
            '<p class="library-description">原文、讲解与推导，放在一起。所有笔记都已替你整理好。</p>'
            '<input id="library-search" type="search" placeholder="搜索课程或笔记" aria-label="搜索课程或笔记">'
            '<div class="library-grid">' + content +
            '</div><p id="no-results" hidden>没有找到对应的笔记。</p></main>'
            '<script>document.querySelector("#library-search").addEventListener("input",function(){'
            'let count=0;document.querySelectorAll(".library-card").forEach(card=>{'
            'card.hidden=!card.dataset.search.toLowerCase().includes(this.value.toLowerCase());'
            'if(!card.hidden)count++});document.querySelector("#no-results").hidden=count>0||'
            '!document.querySelector(".library-card")});</script></body></html>')
    write_atomic(root / "index.html", page)
    command = '#!/bin/sh\ncd -- "$(dirname -- "$0")" || exit 1\n'
    command += 'if command -v open >/dev/null 2>&1; then open index.html; '
    command += 'elif command -v xdg-open >/dev/null 2>&1; then xdg-open index.html; '
    command += 'else printf "%s\\n" "Open index.html in your browser."; fi\n'
    write_atomic(root / "打开笔记.command", command)
    (root / "打开笔记.command").chmod(0o755)
    write_atomic(root / "打开笔记.cmd", '@echo off\r\nstart "" "%~dp0index.html"\r\n')


def doctor(args):
    import importlib.util
    return {"python": sys.version.split()[0], "python_supported": sys.version_info >= (3, 10),
            "pdf_runtime": bool(importlib.util.find_spec("pypdfium2")),
            "offline_math": (PACKAGE / "assets/vendor/mathjax-tex-svg.js").is_file(),
            "needs_agent_tools": ["read source images", "write teaching files",
                                 "execute Python", "inspect HTML in a browser"],
            "model_api_calls": False}


def main():
    parser = argparse.ArgumentParser(description="Portable course-notes mechanics; no model API.")
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("doctor")
    command = subs.add_parser("init")
    command.add_argument("--workspace", required=True)
    command = subs.add_parser("prepare")
    command.add_argument("--workspace", required=True)
    command.add_argument("--pdf", required=True)
    command.add_argument("--pages")
    for name in ("check", "render", "publish"):
        command = subs.add_parser(name)
        command.add_argument("--workspace", required=True)
        command.add_argument("--manifest", required=True)
        command.add_argument("--lesson", required=True)
        if name == "publish":
            command.add_argument("--review", required=True)
            command.add_argument("--qa", required=True)
    args = parser.parse_args()
    try:
        if args.command == "doctor":
            result = doctor(args)
        elif args.command == "init":
            result = {"workspace": str(init(args.workspace))}
        elif args.command == "prepare":
            result = prepare(args)
        elif args.command == "check":
            manifest, lesson = load_lesson(args.workspace, args.manifest, args.lesson)
            result = {"structure": "passed", "semantic_review": "not_determined",
                      "pages": len(lesson["pages"]),
                      "lesson_sha256": digest(Path(args.lesson).read_bytes())}
        elif args.command == "render":
            result = render(args)
        else:
            result = publish(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (NoteError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
