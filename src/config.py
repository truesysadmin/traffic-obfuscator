import os
import logging

class Config:
    """
    Configuration management.
    Now supports reading targets from an external file mounted in Docker.
    """
    
    # Fallback list in case file is missing
    DEFAULT_TARGETS = [
        "https://www.google.com", 
        "https://www.github.com",
        "https://www.amazon.com"
    ]

    @staticmethod
    def get_targets() -> list[str]:
        """
        Loads targets from file if it exists.
        Priority: 
        1. Environment variable TARGETS_FILE
        2. /app/targets.txt (Docker default)
        3. ./targets.txt (Local default)
        """
        file_path = os.getenv("TARGETS_FILE", "/app/targets.txt")
        
        # If default doesn't exist, try local relative path
        if not os.path.exists(file_path) and os.path.exists("targets.txt"):
            file_path = "targets.txt"

        # Priority 1: Read from file (Best for large lists)
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    # Filter out comments (#) and empty lines
                    targets = [
                        line.strip() 
                        for line in f 
                        if line.strip() and not line.strip().startswith("#")
                    ]
                if targets:
                    logging.info(f"Loaded {len(targets)} targets from file.")
                    return targets
            except Exception as e:
                logging.error(f"Failed to read targets file: {e}")

        # Priority 2: Environment variable (Legacy support)
        targets_env = os.getenv("TARGET_URLS")
        if targets_env:
            return [t.strip() for t in targets_env.split(",") if t.strip()]

        # Priority 3: Hardcoded defaults
        return Config.DEFAULT_TARGETS

    @staticmethod
    def get_concurrency() -> int:
        return int(os.getenv("CONCURRENCY", "3"))

    @staticmethod
    def is_headless() -> bool:
        return os.getenv("HEADLESS", "true").lower() == "true"
