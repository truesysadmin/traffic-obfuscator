import asyncio
import os
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
        # Chromium keeps growing when one instance lives for days; relaunch it
        # after this many sessions so memory returns to the baseline.
        self.recycle_after = int(os.getenv("BROWSER_RECYCLE_SESSIONS", "20"))
        # Upper bound for one visit (goto 45s + scrolling + reading is ~90s).
        self.session_timeout = int(os.getenv("SESSION_TIMEOUT_SECONDS", "180"))

    async def _launch(self, p):
        return await p.chromium.launch(
            headless=self.headless,
            args=["--disable-dev-shm-usage"],
        )

    async def _visit(self, page, target_url: str):
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

    async def _browse_target(self, browser, target_url: str) -> bool:
        """One session. Returns False when the browser has to be relaunched."""
        # A fresh context per session: cookies, cache and page state are dropped
        # when it closes instead of piling up in the long-lived browser.
        healthy = True
        context = None
        try:
            context = await asyncio.wait_for(browser.new_context(), 30)
            page = await asyncio.wait_for(context.new_page(), 30)
            crashed = asyncio.Event()
            page.on("crash", lambda _: crashed.set())
            # A renderer killed by the OOM killer leaves page calls such as
            # mouse.wheel waiting forever, so the whole visit is bounded.
            visit = asyncio.ensure_future(self._visit(page, target_url))
            crash = asyncio.ensure_future(crashed.wait())
            done, _ = await asyncio.wait({visit, crash}, timeout=self.session_timeout,
                                         return_when=asyncio.FIRST_COMPLETED)
            for t in (visit, crash):
                t.cancel()
            if visit in done:
                visit.result()
            else:
                healthy = False
                logging.error("Page crashed." if crash in done
                              else f"Session hung for {self.session_timeout}s.")
        except Exception as e:
            logging.error(f"Navigation error: {e}")
        finally:
            if context is not None:
                try:
                    await asyncio.wait_for(context.close(), 15)
                except Exception:
                    healthy = False
        return healthy

    async def run(self):
        logging.info(f"Starting Heavy Generator ({self.scheduler.tz_name}).")
        async with async_playwright() as p:
            browser = await self._launch(p)
            sessions = 0
            healthy = True
            while True:
                # Check sleep before picking a target
                sleep_needed = self.scheduler.get_sleep_time()
                if sleep_needed > 0:
                    logging.info(f"💤 Sleeping for {sleep_needed/3600:.1f} hours...")
                    await asyncio.sleep(sleep_needed)
                    continue

                # Relaunch after N sessions, or after a crashed or hung session.
                if sessions >= self.recycle_after or not healthy or not browser.is_connected():
                    logging.info(f"Relaunching browser after {sessions} sessions.")
                    try:
                        await asyncio.wait_for(browser.close(), 30)
                    except Exception:
                        pass
                    browser = await self._launch(p)
                    sessions = 0

                target = random.choice(self.targets)
                healthy = await self._browse_target(browser, target)
                sessions += 1

                # Much longer wait between targets
                wait_time = random.uniform(60.0, 180.0)
                logging.info(f"Session finished. Waiting {wait_time/60:.1f} minutes...")
                await asyncio.sleep(wait_time)

if __name__ == "__main__":
    try:
        asyncio.run(HeavyTrafficGenerator().run())
    except KeyboardInterrupt:
        pass
