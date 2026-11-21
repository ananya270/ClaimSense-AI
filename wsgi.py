"""Production WSGI entrypoint for ClaimSense AI.

Suitable for deployment behind Gunicorn, Waitress, uWSGI, or Nginx edge proxies.
"""
import sys
from pathlib import Path

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import create_app
from backend.config import Config

# Standard WSGI callable for production servers
application = create_app(Config)
app = application

if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT)
