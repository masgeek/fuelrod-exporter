# auto_reload_env.py
import os
from pathlib import Path
from threading import Thread
import time
from dotenv import load_dotenv

# Only enable in development
if os.getenv("FLASK_ENV") == "development":
    ENV_FILE = Path(__file__).parent.parent / ".env"
    DUMMY_FILE = Path(__file__).parent / ".env_reload_dummy.py"
    WATCH_INTERVAL = 1  # seconds

    def watch_env():
        last_mtime = ENV_FILE.stat().st_mtime if ENV_FILE.exists() else 0
        while True:
            time.sleep(WATCH_INTERVAL)
            if not ENV_FILE.exists():
                continue
            mtime = ENV_FILE.stat().st_mtime
            if mtime != last_mtime:
                print(".env changed, reloading development environment...")
                load_dotenv(override=True)  # reload env
                DUMMY_FILE.touch()          # trigger Flask reloader
                last_mtime = mtime

    # start watcher in background thread
    Thread(target=watch_env, daemon=True).start()

    # Load initially
    load_dotenv(override=True)
