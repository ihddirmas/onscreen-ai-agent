import { test, expect } from "@playwright/test";

test.describe("Public marketing flows", () => {
  test("landing → pricing page → login navigation", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/OnCUE/i);
    await expect(page.getByRole("heading", { level: 1, name: /on-screen AI/i })).toBeVisible();

    await page.goto("/pricing");
    await expect(page).toHaveURL(/\/pricing/);
    await expect(page.getByRole("heading", { name: "Free" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Pro" })).toBeVisible();

    await page.getByRole("link", { name: /get started/i }).first().click();
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole("heading", { name: "Log in" })).toBeVisible();
  });

  test("login page toggles sign-up mode", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("heading", { name: "Log in" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Log in" })).toBeVisible();

    await page.locator("a", { hasText: "Sign up" }).click();
    await expect(page.getByRole("heading", { name: "Create your account" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Sign up" })).toBeVisible();

    await page.locator("a", { hasText: "Log in" }).last().click();
    await expect(page.getByRole("heading", { name: "Log in" })).toBeVisible();
  });

  test("download page loads", async ({ page }) => {
    await page.goto("/download");
    await expect(page.getByRole("heading", { name: "Download OnCUE" })).toBeVisible();
    await expect(page.getByRole("link", { name: /windows/i })).toBeVisible();
  });

  test("persona sections render on landing", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("FOR STUDENTS")).toBeVisible();
    await expect(page.getByText("FOR EARLY-CAREER DEVELOPERS")).toBeVisible();
    await expect(page.getByText("FOR ANYONE WHO THINKS IN HINGLISH")).toBeVisible();
  });

  test("landing pricing section shows tiers", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Pricing", exact: true })).toBeVisible();
    await expect(page.getByRole("link", { name: "Start free" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Choose Pro" })).toBeVisible();
  });
});

test.describe("Auth-gated flows (UI only — no live Supabase)", () => {
  test("unauthenticated dashboard redirects to login", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login/);
  });
});
