#!/usr/bin/env node
// Optional real-browser checks. An agent may instead inspect with its native browser tools.
import fs from "node:fs/promises";
import path from "node:path";
import {pathToFileURL} from "node:url";
import {createHash} from "node:crypto";
import {createRequire} from "node:module";
const args = Object.fromEntries(process.argv.slice(2).reduce((pairs, value, i, values) => {
  if (value.startsWith("--")) pairs.push([value.slice(2), values[i + 1]]);
  return pairs;
}, []));
if (!args.html || !args.lesson || !args.output) {
  throw Error("Use --html preview.html --lesson lesson.json --output browser-review.json " +
              "[--playwright /path/to/playwright] [--chromium /path/to/chromium] [--screenshots directory]");
}
const require = createRequire(import.meta.url);
const {chromium} = require(args.playwright || "playwright");
const digest = value => createHash("sha256").update(value).digest("hex");
const html = await fs.readFile(args.html);
const lessonBytes = await fs.readFile(args.lesson);
const lesson = JSON.parse(lessonBytes);
const browser = await chromium.launch({headless: true,
  ...(args.chromium ? {executablePath: args.chromium} : {})});
const findings = [], errors = [], external = [], screenshots = [];
const viewports = [{width:1280,height:800},{width:1100,height:720},
                   {width:1144,height:654},{width:390,height:844}];
const check = (condition, message) => {
  findings.push({passed:!!condition, message});
  if (!condition) throw Error(message);
};
try {
  const context = await browser.newContext();
  const page = await context.newPage();
  page.on("pageerror", error => errors.push(error.message));
  page.on("request", request => {
    if (/^https?:/i.test(request.url())) external.push(request.url());
  });
  if (args.screenshots) await fs.mkdir(args.screenshots, {recursive:true});
  for (const viewport of viewports) {
    await page.setViewportSize(viewport);
    await page.goto(pathToFileURL(path.resolve(args.html)).href);
    await page.waitForFunction(() => document.documentElement.dataset.readerReady === "true");
    await page.evaluate(async () => {await window.MathJax.startup.promise;});
    check(await page.locator("mjx-merror,[data-mjx-error]").count() === 0,
          viewport.width + ": no formula rendering errors");
    check(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1),
          viewport.width + ": no page-level horizontal overflow");
    check(await page.locator(".equation").evaluateAll(elements =>
      elements.every(el => el.scrollWidth <= el.clientWidth + 2)),
      viewport.width + ": display equations remain fully visible");
    for (const slide of lesson.pages) {
      const unit = page.locator("#page-" + slide.page);
      const source = unit.locator(".source-column");
      const canvas = unit.locator(".source-canvas");
      const rail = unit.locator(".teaching-rail");
      check(await source.evaluate(el => el.scrollHeight <= el.clientHeight + 2),
            viewport.width + "/" + slide.page + ": complete source has no local scrolling");
      if (viewport.width > 780) {
        const left = await source.boundingBox(), right = await rail.boundingBox();
        check(right.x >= left.x + left.width - 2,
              viewport.width + "/" + slide.page + ": source and teaching are paired");
      }
      for (const point of slide.points) {
        await unit.evaluate(el => el.scrollIntoView({block:"start",behavior:"instant"}));
        await unit.locator('.source-badge[data-point="' + point.id + '"]').click();
        check(await unit.getAttribute("data-active-point") === point.id,
              viewport.width + "/" + point.id + ": badge activates matching teaching");
        await unit.evaluate(el => el.scrollIntoView({block:"start",behavior:"instant"}));
        const box = await canvas.boundingBox();
        const [x,y,w,h] = point.region;
        await page.mouse.click(box.x + (x+w/2)*box.width, box.y + (y+h/2)*box.height);
        check(await unit.getAttribute("data-active-point") === point.id,
              viewport.width + "/" + point.id + ": frame interior activates matching teaching");
        if (viewport.width > 780) {
          check(await page.locator("#" + point.id).evaluate(article => {
            const a=article.getBoundingClientRect(), r=article.closest(".teaching-rail").getBoundingClientRect();
            return a.top>=r.top-2 && a.top<r.bottom-10;
          }), viewport.width + "/" + point.id + ": selected lesson heading is visible");
        }
        if (args.screenshots) {
          const filename = path.join(args.screenshots, viewport.width + "-" + point.id + ".png");
          await (viewport.width <= 780 ? page.locator("#" + point.id) : unit).screenshot({path:filename});
          screenshots.push(path.resolve(filename));
        }
      }
      if (viewport.width > 780) {
        const overflowing = await rail.evaluate(el => el.scrollHeight > el.clientHeight + 2);
        if (overflowing) {
          await unit.evaluate(el => el.scrollIntoView({block:"start",behavior:"instant"}));
          await rail.evaluate(el => el.scrollTop=0);
          const box = await rail.boundingBox();
          const before = await page.evaluate(() => window.scrollY);
          await page.mouse.move(box.x+box.width/2, Math.min(box.y+100, viewport.height-20));
          await page.mouse.wheel(0,220);
          await page.waitForTimeout(180);
          check(await rail.evaluate(el => el.scrollTop)>0,
                viewport.width + "/" + slide.page + ": teaching rail scrolls");
          check(Math.abs(await page.evaluate(() => window.scrollY)-before)<3,
                viewport.width + "/" + slide.page + ": rail scrolling leaves outer page stable");
        }
      }
    }
    if (viewport.width > 780) {
      const second = page.locator(".slide-unit").nth(Math.min(1,lesson.pages.length-1));
      await second.evaluate(el=>el.scrollIntoView({block:"start",behavior:"instant"}));
      const before = await page.evaluate(()=>window.scrollY);
      const box = await second.locator(".source-canvas").boundingBox();
      await page.mouse.move(box.x+box.width/2,Math.min(box.y+80,viewport.height-40));
      await page.mouse.wheel(0,190);
      await page.waitForTimeout(180);
      check(await page.evaluate(()=>window.scrollY)>before,
            viewport.width + ": wheel over source moves outer page");
    }
    const firstZoom = page.locator(".zoom-source").first();
    await firstZoom.click();
    check(await page.locator("#source-zoom").evaluate(el=>el.open), "Source zoom opens");
    await page.keyboard.press("Escape");
    check(!await page.locator("#source-zoom").evaluate(el=>el.open), "Source zoom closes");
    const wasDark=await page.locator("body").evaluate(el=>el.classList.contains("dark"));
    await page.locator("#toggle-theme").click();
    check(await page.locator("body").evaluate(el=>el.classList.contains("dark")) !== wasDark,
          viewport.width + ": theme control works");
    await page.locator("#toggle-theme").click();
    await page.locator("#toggle-navigation").click();
    check(await page.locator(".page-navigation").isVisible() === (viewport.width<=780),
          viewport.width + ": directory visibility control works");
    await page.locator("#toggle-navigation").click();
    if (viewport.width<=780 && args.screenshots) {
      for (const slide of lesson.pages) {
        const unit=page.locator("#page-"+slide.page);
        for (const selector of [".source-column",".outcomes"]) {
          if (!await unit.locator(selector).count()) continue;
          const filename=path.join(args.screenshots,viewport.width+"-page-"+slide.page+
            selector.replace(".","-")+".png");
          await unit.locator(selector).screenshot({path:filename});
          screenshots.push(path.resolve(filename));
        }
      }
    }
  }
  await page.emulateMedia({media:"print"});
  check(await page.locator(".source-canvas>img").count() === lesson.pages.length,
        "Print retains exactly one original image per selected page");
  check(await page.locator(".teaching-rail").evaluateAll(elements =>
    elements.every(el => getComputedStyle(el).overflowY === "visible")),
    "Print exposes all teaching instead of clipping the scroll rail");
  check(external.length === 0,"All reading assets work without external requests");
  check(errors.length === 0,"No browser script errors: " + errors.join("; "));
  const result = {schema:1,status:"passed",lesson_sha256:digest(lessonBytes),
    html_sha256:digest(html),inspected_pages:lesson.pages.map(v=>v.page),
    checks:{source_visible:true,point_links:true,rail_scroll:true,outer_scroll:true,
      math_readable:true,responsive_layout:true,no_external_requests:true},
    evidence:"Real Chromium checks across " + viewports.map(v=>v.width+"x"+v.height).join(", ") +
      "; all " + lesson.pages.reduce((n,p)=>n+p.points.length,0) +
      " point badges/interiors tested per viewport. Automated geometry and behavior passed. " +
      "The author must separately inspect the screenshots for source-mark placement and teaching readability.",
    visual_review:{status:"pending",inspected_pages:[],
      evidence:"Inspect the actual screenshots before marking this dimension passed."},
    automated_findings:findings, screenshots};
  await fs.writeFile(args.output,JSON.stringify(result,null,2)+"\n");
  console.log(JSON.stringify({status:result.status,checks:findings.length,screenshots:screenshots.length,
    output:path.resolve(args.output)},null,2));
} finally {
  await browser.close();
}
