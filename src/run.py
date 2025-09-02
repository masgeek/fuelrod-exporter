"""
This script initializes and runs a Flask web application.

Steps:
1. Loads environment variables from `.env`.
2. Creates the Flask app using `create_app()`.
3. If in debug mode, activates auto-reload via `watch_env`.
4. Runs the Flask app with specified host, port, and debug mode.

Environment Variables:
- FLASK_DEBUG
- SERVER_HOST
- SERVER_PORT

Usage:
    $ python run.py
"""

import os
from dotenv import load_dotenv
from fuelrod_exporter.core.auto_reload import watch_env
from fuelrod_exporter.app import get_app as create_app

load_dotenv()

app = create_app()
app.app_context().push()

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG") == "1"
    host = os.getenv("SERVER_HOST", default="0.0.0.0")
    port = int(os.getenv("SERVER_PORT", default=3000))
    app.run(host=host, port=port, debug=debug)
