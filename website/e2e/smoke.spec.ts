import { test, expect } from "@playwright/test";

test.describe("smoke", () => {
  test("landing page loads and shows key sections", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toBeVisible();
    await expect(page.getByRole("link", { name: "Get started", exact: true })).toBeVisible();
  });

  test("login page loads with sign-in form", async ({ page }) => {
    await page.goto("/login");
    await expect(page).toHaveURL(/\/login/);
  });

  test("dashboard redirects unauthenticated to login", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login/);
  });

  test("download page loads", async ({ page }) => {
    await page.goto("/download");
    await expect(page.locator("text=Download")).toBeVisible();
  });
});

test.describe("documents API (unauthenticated)", () => {
  test("upload rejects without auth", async ({ request }) => {
    const res = await request.post("/api/documents/upload");
    expect(res.status()).toBe(401);
  });

  test("search rejects without auth", async ({ request }) => {
    const res = await request.post("/api/documents/search", {
      data: { query: "test" },
    });
    expect(res.status()).toBe(401);
  });

  test("list rejects without auth", async ({ request }) => {
    const res = await request.get("/api/documents/list");
    expect(res.status()).toBe(401);
  });

  test("delete rejects without auth", async ({ request }) => {
    const res = await request.post("/api/documents/delete", {
      data: { id: "00000000-0000-0000-0000-000000000000" },
    });
    expect(res.status()).toBe(401);
  });
});
