import asyncio
import random
import logging
from playwright.async_api import async_playwright
from src.config import Config
from src.scheduler import HumanScheduler

logging.basicConfig(level=logging.INFO, format='[HEAVY-CHAFF] %(message)s')

class HeavyTrafficGenerator:
    def __init__(self):
        self.targets = Config.get_targets()
        self.headless = Config.is_headless()
        self.scheduler = HumanScheduler()

    async def _browse_target(self, browser, target_url: str):
        # --- CIRCADIAN RHYTHM CHECK ---
        sleep_needed = self.scheduler.get_sleep_time()
        if sleep_needed > 0:
            await asyncio.sleep(sleep_needed)
            return # Skip this cycle
        # ------------------------------

        page = await browser.new_page()
        try:
            logging.info(f"Navigating to {target_url}")
            await page.goto(target_url, timeout=45000, wait_until="domcontentloaded")

            # Simulate human behavior
            for _ in range(random.randint(3, 8)):
                scroll_amount = random.randint(200, 800)
                await page.mouse.wheel(0, scroll_amount)
                # Longer pause between scrolls
                await asyncio.sleep(random.uniform(1.5, 4.0))

            # Stay on page for a while (reading time)
            await asyncio.sleep(random.uniform(5.0, 15.0))

        except Exception as e:
            logging.error(f"Navigation error: {e}")
        finally:
            await page.close()

    async def run(self):
        logging.info(f"Starting Heavy Generator ({self.scheduler.tz_name}).")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            while True:
                # Check sleep before picking a target
                sleep_needed = self.scheduler.get_sleep_time()
                if sleep_needed > 0:
                    logging.info(f"💤 Sleeping for {sleep_needed/3600:.1f} hours...")
                    await asyncio.sleep(sleep_needed)
                    continue

                target = random.choice(self.targets)
                await self._browse_target(browser, target)

                # Much longer wait between targets
                wait_time = random.uniform(60.0, 180.0)
                logging.info(f"Session finished. Waiting {wait_time/60:.1f} minutes...")
                await asyncio.sleep(wait_time)

if __name__ == "__main__":
    try:
        asyncio.run(HeavyTrafficGenerator().run())
    except KeyboardInterrupt:
        pass
