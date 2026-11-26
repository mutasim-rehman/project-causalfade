import { expect, test } from "@playwright/test";
import cohorts from "../public/data/cohorts.json";

const sections = [
  "/", "/journey/", "/causal-lab/", "/experimental-design/", "/statistics/", "/cohorts/",
  "/models/", "/decisions/", "/methodology/", "/responses/", "/hypotheses/", "/literature/",
  "/reproducibility/", "/findings/", "/paper/", "/presentation/",
];

for (const viewport of [{ width: 1440, height: 900 }, { width: 1024, height: 768 }, { width: 390, height: 844 }]) {
  test(`all sections render at ${viewport.width} × ${viewport.height}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    for (const path of sections) {
      const response = await page.goto(path);
      expect(response?.ok(), path).toBe(true);
      await expect(page.getByRole("heading", { level: 1 }), path).toBeVisible();
      const dimensions = await page.evaluate(() => ({
        viewport: document.documentElement.clientWidth,
        document: document.documentElement.scrollWidth,
      }));
      expect(dimensions.document, path).toBeLessThanOrEqual(dimensions.viewport + 1);
    }
    expect(errors).toEqual([]);
  });
}

test("cohort links resolve and global search opens the interrupted cohort", async ({ page, request }) => {
  const statuses = await Promise.all(cohorts.cohorts.map(async ({ cohort_id }) =>
    (await request.get(`/cohorts/${cohort_id}/`)).status()
  ));
  expect(statuses.every((status) => status === 200)).toBe(true);
  await page.goto("/");
  await page.getByRole("button", { name: "Search sections and cohorts" }).click();
  const query = page.getByRole("textbox", { name: "Search sections and cohorts" });
  await query.fill("cohort_008");
  await expect(page.getByRole("dialog").getByRole("button", { name: /cohort_008/ })).toBeVisible();
  await query.press("Enter");
  await expect(page).toHaveURL(/\/cohorts\/cohort_008\/$/);
  await expect(page.getByRole("button", { name: /cohort_008.*Interrupted run/ })).toHaveAttribute("aria-pressed", "true");
  await page.getByRole("combobox", { name: "Compare with another cohort" }).selectOption("cohort_029");
  await expect(page).toHaveURL(/compare=cohort_029/);
  await expect(page.getByText(/Incompatible Experimental Designs/)).toBeVisible();
});

test("presentation returns from the causal lab and opens evidence", async ({ page }) => {
  await page.goto("/presentation/?slide=4");
  const slide = page.getByRole("heading", { name: "A different population can require a different action" });
  await expect(slide).toBeVisible();
  await page.getByRole("button", { name: "Open interactive causal lab" }).click();
  await expect(page.getByRole("heading", { name: "Causal Inference Laboratory" })).toBeVisible();
  await page.getByRole("button", { name: "Historical (Confounded)" }).click();
  await expect(page.getByText("Confounding (1+2U)/4", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Return to slide 4" }).click();
  await expect(slide).toBeVisible();
  await page.goto("/presentation/?slide=9");
  await page.getByRole("button", { name: "View evidence" }).click();
  const drawer = page.getByRole("dialog", { name: "Evidence Inspector" });
  await expect(drawer).toBeVisible();
  await expect(drawer.getByText("3 / 256", { exact: true })).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(drawer).toBeHidden();
  await page.keyboard.press("ArrowRight");
  await expect(page).toHaveURL(/slide=10$/);
});

test("transition filters and historical response export use the loaded records", async ({ page }) => {
  await page.goto("/decisions/");
  await expect(page.getByText("Causal · 512 pairs", { exact: true })).toBeVisible();
  await page.getByLabel("Numerical family").selectOption("96");
  await expect(page.getByText("Causal · 4 pairs", { exact: true })).toBeVisible();
  await page.goto("/responses/");
  await page.getByLabel("Archive", { exact: true }).selectOption("cohort_008_interrupted");
  await expect(page.getByText("Showing 26 records", { exact: true })).toBeVisible();
  await page.getByLabel("Scoring outcome").selectOption("UNAVAILABLE");
  await expect(page.getByText("Showing 1 records", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: /interrupted.*Unscored/i }).click();
  await expect(page.getByText(/KeyboardInterrupt/)).toBeVisible();
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export filtered chunk (CSV)" }).click();
  expect((await download).suggestedFilename()).toMatch(/\.csv$/);
});

test("the response inspector resolves the opposite target in the frozen pair", async ({ page }) => {
  await page.goto("/responses/");
  await expect(page.getByText("Showing 1024 records", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: /Gold:.*Pred:/ }).first().click();
  await page.getByRole("button", { name: "Compare matched target" }).click();
  await expect(page.getByRole("heading", { name: "Target 0", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Target 1", exact: true })).toBeVisible();
});

test("the themed overview chart renders and exports an SVG", async ({ page }) => {
  await page.goto("/");
  const svg = page.getByRole("button", { name: "SVG", exact: true });
  await expect(svg).toBeEnabled();
  await expect(page.locator("svg text").filter({ hasText: "25.00%" })).toBeVisible();
  await page.getByRole("button", { name: "Toggle theme" }).click();
  await expect(page.locator("html")).not.toHaveClass(/\bdark\b/);
  const download = page.waitForEvent("download");
  await svg.click();
  expect((await download).suggestedFilename()).toBe("cohort-029-primary-fidelity.svg");
  await page.reload();
  await expect(page.locator("html")).not.toHaveClass(/\bdark\b/);
});

test("Cohort 024 keeps task correctness and action validity visible across prompt conditions", async ({ page }) => {
  await page.goto("/models/");
  const matrix = page.getByRole("table").first();
  const qwen = matrix.getByRole("row", { name: /qwen7b/i });
  await expect(qwen.getByText("111/256 correct", { exact: true })).toBeVisible();
  await page.getByLabel("Task and prompt condition").selectOption("decision|neutral");
  await expect(qwen.getByText("144/256 correct", { exact: true })).toBeVisible();
  await expect(qwen.getByText("256/256 valid", { exact: true }).first()).toBeVisible();
});
