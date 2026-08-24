"use strict";

const searchInput = document.querySelector("[data-catalog-search]");
const filters = [...document.querySelectorAll("[data-catalog-filter]")];
const entries = [...document.querySelectorAll("[data-catalog-entry]")];
const count = document.querySelector("[data-catalog-count]");
const empty = document.querySelector("[data-catalog-empty]");
let activeKind = "all";

function normalize(value) {
  return value.trim().replace(/\s+/g, " ").toLocaleLowerCase("zh-Hant");
}

function applyCatalogFilters() {
  const query = normalize(searchInput?.value ?? "");
  let visible = 0;
  for (const entry of entries) {
    const kindMatches = activeKind === "all" || entry.dataset.kind === activeKind;
    const textMatches = normalize(entry.dataset.search ?? "").includes(query);
    entry.hidden = !(kindMatches && textMatches);
    if (!entry.hidden) visible += 1;
  }
  if (count) count.textContent = String(visible);
  if (empty) empty.hidden = visible !== 0;
}

searchInput?.addEventListener("input", applyCatalogFilters);
for (const filter of filters) {
  filter.addEventListener("click", () => {
    activeKind = filter.dataset.catalogFilter ?? "all";
    for (const candidate of filters) {
      candidate.setAttribute("aria-pressed", String(candidate === filter));
    }
    applyCatalogFilters();
  });
}
