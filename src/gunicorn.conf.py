import os
from dotenv import load_dotenv
import gunicorn

load_dotenv()

# 🛠 Bind address
bind = f"{os.getenv('SERVER_IP', '0.0.0.0')}:{os.getenv('SERVER_PORT', '3000')}"

# 📁 Log directory outside src
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
os.makedirs(log_dir, exist_ok=True)

accesslog = os.path.join(log_dir, "gunicorn-access.log")
errorlog = os.path.join(log_dir, "gunicorn-error.log")
capture_output = True

# 🧵 Worker config
workers = int(os.getenv("WORKERS", "2"))
worker_class = os.getenv("WORKER_CLASS", "sync")
timeout = int(os.getenv("WORKER_TIMEOUT", "30"))
graceful_timeout = int(os.getenv("GRACEFUL_TIMEOUT", "30"))
loglevel = os.getenv("LOG_LEVEL", "info").lower()

# 🔒 Optional SSL
# keyfile = os.getenv("SSL_KEY_PATH")
# certfile = os.getenv("SSL_CERT_PATH")

# 🧼 Suppress Gunicorn banner
gunicorn.SERVER_SOFTWARE = ""