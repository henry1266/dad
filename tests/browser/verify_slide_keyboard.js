async (page) => {
  const consoleErrors = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  page.on("pageerror", (error) => consoleErrors.push(`pageerror: ${error.message}`));

  const state = (label) => page.evaluate((currentLabel) => {
    const active = document.activeElement;
    let control = active?.tagName ?? "NONE";
    if (active?.matches(".slide-toolbar__home")) control = "home";
    if (active?.hasAttribute("data-slide-prev")) control = "prev";
    if (active?.hasAttribute("data-slide-next")) control = "next";
    if (active?.hasAttribute("data-slide-help-toggle")) control = "help";
    return {
      label: currentLabel,
      control,
      progress: document.querySelector("[data-slide-progress]")?.textContent,
      helpHidden: document.querySelector("[data-slide-help]")?.hidden,
    };
  }, label);
  const assert = (condition, message) => {
    if (!condition) throw new Error(message);
  };
  const expectState = async (label, expected) => {
    const actual = await state(label);
    for (const [key, value] of Object.entries(expected)) {
      assert(actual[key] === value, `${label}: expected ${key}=${value}, got ${actual[key]}`);
    }
    evidence.push(actual);
  };
  const waitForProgress = (expected) => page.waitForFunction((value) => {
    return document.querySelector("[data-slide-progress]")?.textContent === value;
  }, expected);

  const evidence = [];
  await page.goto(page.url().split("#")[0]);
  const initialProgress = await page.locator("[data-slide-progress]").textContent();
  const total = initialProgress.split("/")[1].trim();
  const progress = (number) => `${number} / ${total}`;

  await expectState("initial", { control: "BODY", progress: progress(1) });
  await page.keyboard.press("Tab");
  await expectState("tab-to-home", { control: "home", progress: progress(1) });
  await page.keyboard.press("Tab");
  await expectState("tab-to-prev", { control: "prev", progress: progress(1) });
  await page.keyboard.press("Tab");
  await expectState("tab-to-next", { control: "next", progress: progress(1) });
  await page.keyboard.press("Shift+Tab");
  await expectState("shift-tab-to-prev", { control: "prev", progress: progress(1) });

  await page.keyboard.press("Tab");
  await expectState("tab-forward-to-next", { control: "next", progress: progress(1) });
  await page.keyboard.press("Space");
  await waitForProgress(progress(2));
  await expectState("space-activates-next-once", { control: "next", progress: progress(2) });
  await page.keyboard.press("Enter");
  await waitForProgress(progress(3));
  await expectState("enter-activates-next-once", { control: "next", progress: progress(3) });

  await page.keyboard.press("Tab");
  await expectState("tab-to-help", { control: "help", progress: progress(3) });
  await page.keyboard.press("Space");
  await expectState("space-opens-help", {
    control: "help",
    progress: progress(3),
    helpHidden: false,
  });
  await page.keyboard.press("Space");
  await expectState("space-closes-help", {
    control: "help",
    progress: progress(3),
    helpHidden: true,
  });
  await page.keyboard.press("Enter");
  await expectState("enter-opens-help", {
    control: "help",
    progress: progress(3),
    helpHidden: false,
  });
  await page.keyboard.press("Escape");
  await expectState("escape-closes-help", {
    control: "help",
    progress: progress(3),
    helpHidden: true,
  });

  await page.evaluate(() => document.activeElement?.blur());
  await expectState("focus-outside-controls", { control: "BODY", progress: progress(3) });
  await page.keyboard.press("ArrowRight");
  await waitForProgress(progress(4));
  await expectState("arrow-right-advances-outside", { control: "BODY", progress: progress(4) });
  await page.keyboard.press("PageDown");
  await waitForProgress(progress(5));
  await expectState("page-down-advances-outside", { control: "BODY", progress: progress(5) });
  await page.keyboard.press("ArrowLeft");
  await waitForProgress(progress(4));
  await expectState("arrow-left-reverses-outside", { control: "BODY", progress: progress(4) });
  await page.keyboard.press("PageUp");
  await waitForProgress(progress(3));
  await expectState("page-up-reverses-outside", { control: "BODY", progress: progress(3) });
  await page.keyboard.press("Space");
  await waitForProgress(progress(4));
  await expectState("space-advances-outside", { control: "BODY", progress: progress(4) });
  await page.keyboard.press("Tab");
  const globalTabState = await state("global-tab-keeps-progress");
  assert(globalTabState.progress === progress(4), "global Tab must not advance the deck");
  assert(globalTabState.control !== "BODY", "global Tab must move focus");
  evidence.push(globalTabState);

  assert(consoleErrors.length === 0, `console errors: ${consoleErrors.join(" | ")}`);
  return { evidence, consoleErrors };
}
