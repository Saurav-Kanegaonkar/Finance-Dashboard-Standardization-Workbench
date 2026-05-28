import { chromium } from "playwright";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({
  viewport: { width: 1440, height: 980 },
  deviceScaleFactor: 1,
});

const views = [
  ["cockpit", "cockpit.png", "Where finance reporting cleanup should start"],
  ["standards", "standards-lab.png", "Stakeholder requests mapped to report standards"],
  ["quality", "quality-control.png", "Refresh and source defects blocking trusted reporting"],
  ["sac", "sac-handoff.png", "Planning packets with mapping, currency, and access checks"],
];

await page.goto("http://127.0.0.1:4173", { waitUntil: "networkidle" });

for (const [view, file, expectedText] of views) {
  await page.click(`button[data-view="${view}"]`);
  await page.getByText(expectedText, { exact: true }).waitFor({ timeout: 5000 });
  await page.screenshot({ path: `docs/images/${file}`, fullPage: false });
  if (view === "cockpit") {
    await page.screenshot({ path: "docs/images/dashboard.png", fullPage: false });
  }
}

await browser.close();
console.log(`Captured ${views.length} screenshots.`);
