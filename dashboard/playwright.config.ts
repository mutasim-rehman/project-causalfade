import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  testMatch: "**/*.browser.spec.ts",
  timeout: 60_000,
  use: {
    baseURL: process.env.CAUSALFADE_BASE_URL ?? "http://127.0.0.1:4173",
    channel: process.env.CAUSALFADE_BROWSER_CHANNEL || undefined,
  },
});
