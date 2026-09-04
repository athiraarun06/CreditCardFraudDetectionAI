import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # noqa: E402

# Vercel's Python runtime looks for a module-level ASGI/WSGI callable named `app`.
