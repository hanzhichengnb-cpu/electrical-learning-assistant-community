(function () {
  "use strict";
  const all = (selector, root = document) => [...root.querySelectorAll(selector)];
  function activate(identity, moveRail, movePage) {
    const article = document.getElementById(identity);
    if (!article) return;
    const unit = article.closest(".slide-unit");
    all(".point", unit).forEach(el => el.classList.toggle("active", el.id === identity));
    all(".source-badge", unit).forEach(el => el.classList.toggle("active", el.dataset.point === identity));
    all(".source-outline", unit).forEach(el => el.classList.toggle("active", el.dataset.for === identity));
    const rail = article.closest(".teaching-rail");
    if (moveRail && getComputedStyle(rail).overflowY === "auto") {
      const top = article.getBoundingClientRect().top - rail.getBoundingClientRect().top + rail.scrollTop - 16;
      rail.scrollTo({top, behavior: "auto"});
    } else if (moveRail && window.innerWidth <= 780) {
      article.scrollIntoView({block: "start", behavior: "auto"});
    }
    if (movePage) unit.scrollIntoView({block: "start", behavior: "auto"});
    unit.dataset.activePoint = identity;
  }
  document.addEventListener("click", function (event) {
    const target = event.target.closest("[data-point]");
    if (!target) return;
    let identity = target.dataset.point;
    if (target.classList.contains("source-hit") && event.detail !== 0) {
      const canvas = target.closest(".source-canvas");
      const hits = all(".source-hit", canvas).filter(hit => {
        const box = hit.getBoundingClientRect();
        return event.clientX >= box.left && event.clientX <= box.right &&
               event.clientY >= box.top && event.clientY <= box.bottom;
      }).sort((a, b) => Number(a.dataset.area) - Number(b.dataset.area));
      if (hits.length) identity = hits[0].dataset.point;
    }
    activate(identity, !target.classList.contains("point-number"), false);
  });
  function sizeRails() {
    all(".paired").forEach(pair => {
      const column = pair.querySelector(".source-column");
      pair.style.setProperty("--rail-height", Math.max(300, Math.ceil(column.getBoundingClientRect().height)) + "px");
    });
  }
  const observer = new ResizeObserver(sizeRails);
  all(".source-column").forEach(el => observer.observe(el));
  window.addEventListener("resize", sizeRails);
  window.addEventListener("load", sizeRails);
  sizeRails();
  const current = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        all(".page-navigation a").forEach(a => a.classList.toggle("current", a.hash === "#" + entry.target.id));
      }
    });
  }, {rootMargin: "-12% 0px -62% 0px"});
  all(".slide-unit").forEach(unit => {
    current.observe(unit);
    const first = unit.querySelector(".point");
    if (first) activate(first.id, false, false);
  });
  document.getElementById("toggle-navigation").addEventListener("click", () => {
    document.body.classList.toggle(window.innerWidth <= 780 ? "navigation-mobile-open" : "navigation-hidden");
    requestAnimationFrame(sizeRails);
  });
  const theme = document.getElementById("toggle-theme");
  function setTheme(dark) {
    document.body.classList.toggle("dark", dark);
    theme.textContent = dark ? "浅色" : "深色";
  }
  try {setTheme(localStorage.getItem("course-notes-theme") === "dark");} catch (_) {}
  theme.addEventListener("click", () => {
    const dark = !document.body.classList.contains("dark");
    setTheme(dark);
    try {localStorage.setItem("course-notes-theme", dark ? "dark" : "light");} catch (_) {}
  });
  document.getElementById("print-note").addEventListener("click", () => window.print());
  const zoom = document.getElementById("source-zoom");
  all(".zoom-source").forEach(button => button.addEventListener("click", () => {
    const image = button.closest(".slide-unit").querySelector(".source-canvas>img");
    zoom.querySelector("img").src = image.src;
    zoom.showModal();
  }));
  document.getElementById("close-zoom").addEventListener("click", () => zoom.close());
  zoom.addEventListener("click", event => {if (event.target === zoom) zoom.close();});
  document.documentElement.dataset.readerReady = "true";
}());
