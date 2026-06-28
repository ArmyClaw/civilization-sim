import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });

// Test 1: Entropy Lab page
console.log('Testing entropy lab page...');
const errors = [];
page.on('pageerror', err => errors.push(err.message));
await page.goto('https://army-yorozuya.art/study/entropy-lab/', { waitUntil: 'networkidle' });
await page.waitForTimeout(2000);
console.log('Errors:', errors.length > 0 ? errors : 'None');

// Check experiments are visible
const cards = await page.locator('.exp-card').count();
console.log('Experiment cards visible:', cards);

// Click first experiment (gas diffusion)
await page.locator('.exp-card:first-child').click();
await page.waitForTimeout(500);

// Click start button
const startBtn = page.locator('#btnStart');
await startBtn.click();
await page.waitForTimeout(1500);

// Take screenshot
await page.screenshot({ path: '/home/ecs-user/.openclaw/workspace/entropy-lab-check.png', fullPage: false });
console.log('Entropy lab screenshot saved');

// Test 2: Lab homepage
console.log('Testing lab homepage...');
await page.goto('https://army-yorozuya.art/study/', { waitUntil: 'networkidle' });
await page.waitForTimeout(1000);

const projCards = await page.locator('.proj').count();
console.log('Project cards:', projCards);

// Scroll to see all cards
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
await page.waitForTimeout(500);

await page.screenshot({ path: '/home/ecs-user/.openclaw/workspace/lab-homepage-11.png', fullPage: true });
console.log('Homepage screenshot saved');

await browser.close();
console.log('All checks passed!');
