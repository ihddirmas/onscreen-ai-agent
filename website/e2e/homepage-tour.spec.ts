import { test, expect } from "@playwright/test";

test.use({
  video: "on",
  viewport: { width: 1280, height: 720 },
});

test("OnCUE homepage full scroll tour (desktop buddy)", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("navigation").getByRole("link", { name: /OnCUE/i })).toBeVisible();
  await expect(page.locator("h1")).toContainText(/hotkey/i);
  await expect(page.getByText(/AI buddy on your desktop/i)).toBeVisible();

  const sectionIds = [
    "use-cases",
    "features",
    "hotkeys",
    "how-it-works",
    "integrations",
    "security",
    "developers",
    "pricing",
    "faq",
  ];

  for (const id of sectionIds) {
    await page.evaluate((sectionId) => {
      document.getElementById(sectionId)?.scrollIntoView({ behavior: "instant", block: "start" });
    }, id);
    await page.waitForTimeout(900);
    await expect(page.locator(`#${id}`)).toBeVisible();
  }

  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(1200);
  await expect(page.getByText(/Frequently asked questions/i)).toBeVisible();
});
