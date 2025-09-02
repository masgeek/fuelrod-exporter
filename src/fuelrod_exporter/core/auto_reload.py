# src/module/auto_reload_env.py
import os
import time
from pathlib import Path
from threading import Thread
from dotenv import load_dotenv

# Project root (4 levels up from this file)
ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT_DIR / ".env"
DUMMY_FILE = Path(__file__).parent / ".env_reload_dummy.py"

if os.getenv("FLASK_ENV") == "development":
    WATCH_INTERVAL = float(os.getenv("ENV_WATCH_INTERVAL", "1"))
    VERBOSE = os.getenv("ENV_WATCH_VERBOSE", "false").lower() == "true"

    def watch_env():
        try:
            last_mtime = ENV_FILE.stat().st_mtime if ENV_FILE.exists() else 0
        except FileNotFoundError:
            last_mtime = 0

        if VERBOSE:
            print(f"🔄 Watching {ENV_FILE} for changes...")

        while True:
            time.sleep(WATCH_INTERVAL)
            try:
                mtime = ENV_FILE.stat().st_mtime
            except FileNotFoundError:
                continue

            if mtime != last_mtime:
                print("♻️ .env changed → reloading development environment...")
                load_dotenv(ENV_FILE, override=True)
                DUMMY_FILE.write_text(f"# reload {time.time()}\n")
                last_mtime = mtime

    # Start watcher in background
    Thread(target=watch_env, daemon=True).start()

    # Initial load
    load_dotenv(ENV_FILE, override=True)
else:
    def watch_env():
        print("ℹ️ Not in development mode, skipping .env auto-reload")
