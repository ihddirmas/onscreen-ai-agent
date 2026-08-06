import { test, expect } from "@playwright/test";

const WEBAPP = process.env.WEBAPP_BASE_URL || "http://127.0.0.1:3002";
const WEBAPP_BACKEND = process.env.WEBAPP_BACKEND_URL || "http://127.0.0.1:8002";

test.describe("Reflex webapp public flows", () => {
  test("landing page loads", async ({ page }) => {
    await page.goto(`${WEBAPP}/`);
    await expect(page.getByText("OnCUE", { exact: false }).first()).toBeVisible();
  });

  test("login page toggles sign-up mode", async ({ page }) => {
    await page.goto(`${WEBAPP}/login`);
    await expect(page.getByRole("heading", { name: "Log in" })).toBeVisible();
    await page.getByText("Sign up", { exact: true }).click();
    await expect(page.getByRole("heading", { name: "Create your account" })).toBeVisible();
    await page.getByText("Log in", { exact: true }).click();
    await expect(page.getByRole("heading", { name: "Log in" })).toBeVisible();
  });

  test("download page loads", async ({ page }) => {
    await page.goto(`${WEBAPP}/download`);
    await expect(page.getByText(/download/i).first()).toBeVisible();
  });

  test("backend health ping", async ({ request }) => {
    const res = await request.get(`${WEBAPP_BACKEND}/ping`);
    expect(res.status()).toBe(200);
    expect(await res.text()).toContain("pong");
  });
});
