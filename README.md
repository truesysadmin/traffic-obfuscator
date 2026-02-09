# Traffic Obfuscator

This project was created for a friend who values his privacy and wants to stay under the radar of mass surveillance. 

> "Always strive to do things well and beautifully. Doing it poorly will happen on its own :)" 
> — *My Father's wisdom*

## Overview

Traffic Obfuscator is a tool designed to mask your real web activity by generating "chaff" (noise) traffic. It makes it significantly harder for ISPs or automated tracking systems to build an accurate profile of your interests by mixing your real requests with randomized, human-like browsing patterns.

## Features

- **Circadian Rhythm Scheduler**: Simulates human behavior by following a sleep/wake cycle based on your timezone. It handles late-night sessions (past midnight), randomizes daily start/end times, and respects weekends.
- **Ultra-Slow Light Chaff**: Performs background HTTP requests with radical delays (average 1+ minute per page) and frequent long "reading breaks" (up to 15 minutes) to mimic deep reading.
- **Heavy Chaff (High Realism)**: Uses a real **Chromium browser** (via Playwright) to navigate, scroll, and interact with websites at a very relaxed, human pace.
- **Privacy First**: Uses a rotation of real browser User-Agents and avoids predictable request patterns.

## Quick Start

### 1. Configure Targets
Edit `targets.txt` to add or remove URLs. The system automatically detects this file.

### 2. Build and Run
Use the `Makefile` for easy orchestration:

```bash
# Build the Docker images
make build

# Start the generators in the background
make up

# Watch the activity (Ctrl+C to stop viewing)
make logs
```

### 3. Management & Cleanup
```bash
# Stop the generators
make down

# Complete cleanup (removes containers, images, volumes, and temp files)
make clean
```

## Configuration

Customize behavior in `docker-compose.yml`:
- `TZ`: Your local timezone (e.g., `Europe/Madrid`).
- `CONCURRENCY`: Number of simultaneous light workers (Recommended: `1` or `2` for maximum stealth).
- `HEADLESS`: Set to `true` for background browser operation.

## Deployment as a Service (Linux)

To run this as a permanent background service on a Linux server:

```bash
# Install and start the systemd service
sudo make install

# View service logs
journalctl -u traffic-noise -f

# Uninstall the service
sudo make uninstall
```

---
*Stay safe and keep your digital footprint clean.*
