import asyncio
import random
import logging
import aiohttp
from src.config import Config
from src.scheduler import HumanScheduler

logging.basicConfig(level=logging.INFO, format='[LIGHT-CHAFF] %(message)s')

class LightTrafficGenerator:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (AppleWebKit/537.36; KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    ]

    def __init__(self):
        self.targets = Config.get_targets()
        self.concurrency = Config.get_concurrency()
        self.scheduler = HumanScheduler()

    async def _worker(self, session: aiohttp.ClientSession, worker_id: int):
        # Initial jitter to prevent all workers from hitting targets simultaneously
        await asyncio.sleep(random.uniform(0, 45) * worker_id)
        
        while True:
            # --- CIRCADIAN RHYTHM CHECK ---
            sleep_needed = self.scheduler.get_sleep_time()
            if sleep_needed > 0:
                await asyncio.sleep(sleep_needed + random.uniform(0, 60))
                continue
            # ------------------------------

            # 1. Wait BEFORE request (Human reading/thinking time)
            # Average delay around 75 seconds (1.25 minutes per page)
            delay = abs(random.gauss(75.0, 25.0))
            await asyncio.sleep(delay)

            target = random.choice(self.targets)
            try:
                headers = {"User-Agent": random.choice(self.USER_AGENTS)}
                async with session.get(target, headers=headers, timeout=15) as resp:
                    size = 0
                    async for chunk in resp.content.iter_chunked(1024):
                        size += len(chunk)
                    logging.info(f"Fetched {target} | Status: {resp.status} | Size: {size} bytes")

            except Exception as e:
                logging.debug(f"Error fetching {target}: {e}")

            # 2. Frequent long breaks (45% chance)
            if random.random() < 0.45:
                # Pause from 3 to 15 minutes (real human distractions)
                thinking_time = random.uniform(180.0, 900.0)
                logging.info(f"🤔 Taking a long reading break: {thinking_time/60:.1f} minutes")
                await asyncio.sleep(thinking_time)

    async def run(self):
        logging.info(f"Starting Light Generator ({self.scheduler.tz_name}).")
        async with aiohttp.ClientSession() as session:
            # Note: We recommend setting CONCURRENCY=1 in docker-compose.yml for maximum human-likeness
            tasks = [self._worker(session, i) for i in range(self.concurrency)]
            await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(LightTrafficGenerator().run())
    except KeyboardInterrupt:
        pass
