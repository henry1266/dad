"use strict";

const form = document.querySelector("[data-workspace-form]");
const operations = [...document.querySelectorAll("[data-operation]")];
const customWiki = document.querySelector("[data-custom-wiki]");
const customRange = document.querySelector("[data-custom-range]");
const submit = document.querySelector("[data-workspace-submit]");

function syncWorkspaceState() {
  if (customRange) customRange.disabled = !customWiki?.checked;
  if (submit) submit.disabled = !operations.some(operation => operation.checked);
}

for (const operation of operations) {
  operation.addEventListener("change", syncWorkspaceState);
}
form?.addEventListener("submit", () => {
  if (submit) {
    submit.disabled = true;
    submit.textContent = "處理中…";
  }
});
syncWorkspaceState();
