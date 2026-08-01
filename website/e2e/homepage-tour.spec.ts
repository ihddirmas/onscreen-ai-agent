import { test, expect } from "@playwright/test";

test.use({
  video: "on",
  viewport: { width: 1280, height: 720 },
});

test("OnCUE homepage full scroll tour (v0-import design)", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("navigation").getByRole("link", { name: "OnCUE" })).toBeVisible();
  await expect(page.locator("h1")).toContainText(/Ask your screen/i);

  for (const id of [
    "#features",
    "#how-it-works",
    "#integrations",
    "#security",
    "#developers",
    "#pricing",
  ]) {
    await page.locator(id).scrollIntoViewIfNeeded();
    await page.waitForTimeout(1200);
  }

  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(1500);
  await expect(page.getByText(/OnCUE/i).first()).toBeVisible();
});
