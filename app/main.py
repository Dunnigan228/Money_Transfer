from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.db.session import init_db
from app.api.v1 import auth, accounts, transfers, rates, audit
from app.utils.message_broker import message_broker
from app.utils.telegram_logger import telegram_logger
from app.utils.redis_client import redis_client
from app.utils.rate_limiter import rate_limit_check
import time


@asynccontextmanager
async def lifespan(app: FastAPI):
    await telegram_logger.log_info(f"{settings.app_name} starting up...")

    try:
        await init_db()

        await message_broker.connect()

        await redis_client.connect()

        await telegram_logger.log_success(f"{settings.app_name} started successfully")

    except Exception as e:
        await telegram_logger.log_critical(f"Failed to start application: {str(e)}")
        raise

    yield

    await telegram_logger.log_info(f"{settings.app_name} shutting down...")

    try:
        await message_broker.close()
        await redis_client.disconnect()
        await telegram_logger.log_info(f"{settings.app_name} shut down successfully")
    except Exception as e:
        await telegram_logger.log_error(f"Error during shutdown: {str(e)}")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Money Transfer Service with real-time currency conversion",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path not in ["/health", "/docs", "/redoc", "/openapi.json"]:
        await rate_limit_check(request)
    response = await call_next(request)
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Validation error",
            "data": {"errors": exc.errors()},
        },
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    await telegram_logger.log_error(f"Database error: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Database error occurred",
            "data": None,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    await telegram_logger.log_error(f"Unhandled exception: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Internal server error",
            "data": None,
        },
    )


app.include_router(auth.router, prefix="/api/v1")
app.include_router(accounts.router, prefix="/api/v1")
app.include_router(transfers.router, prefix="/api/v1")
app.include_router(rates.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
    }
