import os
import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.routers import (
    auth, predict, predict_batch, analytics, transactions, metrics,
    feature_importance, retrain, health, meta, alerts, customers, demo,
)
from app.core.rate_limit import rate_limit_middleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("fraud_detection")

APP_VERSION = "2.0.0"

app = FastAPI(
    title="Credit Card Fraud Detection AI System",
    description="Real-time fraud detection platform: ML scoring + business rule engine, "
                 "customer/merchant risk profiles, alert operations center.",
    version=APP_VERSION,
)

# CORS origins are configurable via env (comma-separated). In production, set ALLOWED_ORIGINS
# to your deployed frontend URL(s) explicitly. Local dev matches any localhost/127.0.0.1 port.
_allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = [o.strip() for o in _allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?" if not ALLOWED_ORIGINS else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(rate_limit_middleware)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(f"Unhandled error on {request.method} {request.url.path}")
        raise
    duration_ms = round((time.time() - start) * 1000, 1)
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)")
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.url.path}: {exc}")
    return JSONResponse(status_code=500, content={"detail": f"Internal server error: {exc}"})


app.include_router(health.router)
app.include_router(meta.router)
app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(predict_batch.router)
app.include_router(analytics.router)
app.include_router(transactions.router)
app.include_router(alerts.router)
app.include_router(customers.router)
app.include_router(demo.router)
app.include_router(metrics.router)
app.include_router(feature_importance.router)
app.include_router(retrain.router)


@app.on_event("startup")
def on_startup():
    from app.core.database import init_db, DATABASE_URL
    try:
        init_db()
        logger.info(f"Startup complete. Using database: {DATABASE_URL}")
        logger.info(f"CORS allowed origins: {ALLOWED_ORIGINS}")
    except Exception as e:
        logger.error(f"Database initialization failed at startup: {e}. "
                      f"Endpoints requiring DB will fail until it's reachable.")


from app.core.paths import SAVED_MODELS_DIR
if os.path.isdir(SAVED_MODELS_DIR):
    app.mount("/static/models", StaticFiles(directory=SAVED_MODELS_DIR), name="model_artifacts")


@app.get("/")
def root():
    return {"message": "Credit Card Fraud Detection AI System API", "docs": "/docs", "version": APP_VERSION}
