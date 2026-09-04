"""
Single source of truth for where saved_models/ and data/ live, since that differs by
deployment shape:
  - Local dev / Docker: backend/ sits inside the repo, saved_models/ and data/ are siblings
    of backend/ at the repo root.
  - Vercel (or any deploy where "Root Directory" is set to backend/): only files under
    backend/ are shipped, so saved_models/ and data/ must live INSIDE backend/ instead
    (backend/saved_models/, backend/data/) — gated on the VERCEL/AWS_LAMBDA env vars so
    local dev is unaffected even if a stale copy exists under backend/.
"""
import os

_CORE_DIR = os.path.dirname(os.path.abspath(__file__))          # backend/app/core
_APP_DIR = os.path.dirname(_CORE_DIR)                              # backend/app
BACKEND_DIR = os.path.dirname(_APP_DIR)                            # backend/

_IS_SERVERLESS = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))

PROJECT_ROOT = BACKEND_DIR if _IS_SERVERLESS else os.path.dirname(BACKEND_DIR)
SAVED_MODELS_DIR = os.path.join(PROJECT_ROOT, "saved_models")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
