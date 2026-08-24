"use strict";

const bundledDeckNavigationKeys = new Set([
  " ",
  "Spacebar",
  "PageUp",
  "PageDown",
  "ArrowLeft",
  "ArrowUp",
  "ArrowRight",
  "ArrowDown",
]);

function guardBundledDeckNavigation(event) {
  const target = event.target instanceof Element ? event.target : null;
  const focusIsInControls = target?.closest(".slide-toolbar, [data-slide-help]");
  if (event.key === "Tab" || (focusIsInControls && bundledDeckNavigationKeys.has(event.key))) {
    event.stopImmediatePropagation();
  }
}

document.addEventListener("keydown", guardBundledDeckNavigation);
document.addEventListener("keyup", guardBundledDeckNavigation);

const deck = impress();
deck.init();
const slides = [...document.querySelectorAll("#impress .step.slide")];
const progress = document.querySelector("[data-slide-progress]");
const help = document.querySelector("[data-slide-help]");
const helpToggle = document.querySelector("[data-slide-help-toggle]");

function updateProgress(step) {
  const index = slides.indexOf(step);
  if (progress) progress.textContent = index < 0 ? "總覽" : `${index + 1} / ${slides.length}`;
}

document.querySelector("[data-slide-prev]")?.addEventListener("click", () => deck.prev());
document.querySelector("[data-slide-next]")?.addEventListener("click", () => deck.next());
document.addEventListener("impress:stepenter", event => updateProgress(event.target));
helpToggle?.addEventListener("click", () => {
  const opening = help?.hidden ?? false;
  if (help) help.hidden = !opening;
  helpToggle.setAttribute("aria-expanded", String(opening));
});
document.addEventListener("keydown", event => {
  if (event.key === "Escape" && help && !help.hidden) {
    help.hidden = true;
    helpToggle?.setAttribute("aria-expanded", "false");
  }
});
updateProgress(document.querySelector("#impress .step.active") ?? slides[0]);
