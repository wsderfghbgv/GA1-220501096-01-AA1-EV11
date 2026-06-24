"""
Main application entry point for device_systems API.
Configures FastAPI with CORS, middleware, rate limiting, and route registration.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.database.connection import engine, Base
from app.middlewares.request_middleware import RequestMiddleware

# Import routers
from app.auth.auth_routes import router as auth_router
from app.routes.user_routes import router as user_router
from app.routes.device_routes import router as device_router
from app.routes.loan_routes import router as loan_router

# ─────────────────────────────────────────────────────────
# FastAPI Application Configuration
# ─────────────────────────────────────────────────────────

app = FastAPI(
    title="device_systems API",
    description=(
        "API REST segura para gestión de usuarios, dispositivos y préstamos. "
        "Implementa autenticación OAuth2 con JWT, autorización basada en roles, "
        "middleware personalizado, CORS, rate limiting y validaciones avanzadas con Pydantic v2."
    ),
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Auth",
            "description": "Endpoints de autenticación: registro, login y perfil de usuario."
        },
        {
            "name": "Users",
            "description": "Gestión de usuarios. Requiere autenticación."
        },
        {
            "name": "Devices",
            "description": "CRUD de dispositivos tecnológicos. Operaciones protegidas por rol."
        },
        {
            "name": "Loans",
            "description": "Gestión de préstamos de dispositivos. Requiere autenticación."
        },
    ]
)

# ─────────────────────────────────────────────────────────
# Rate Limiting Configuration (slowapi)
# ─────────────────────────────────────────────────────────

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─────────────────────────────────────────────────────────
# CORS Configuration
# ─────────────────────────────────────────────────────────
# In development, allow specific local origins.
# WARNING: Do not use allow_origins=["*"] with allow_credentials=True in production.
# Using "*" with credentials exposes the API to cross-site request forgery (CSRF)
# attacks, as any website could make authenticated requests on behalf of the user.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite default
        "http://localhost:3000",   # React/Next.js default
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────
# Custom Middleware
# ─────────────────────────────────────────────────────────

app.add_middleware(RequestMiddleware)

# ─────────────────────────────────────────────────────────
# Router Registration
# ─────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(device_router)
app.include_router(loan_router)

# ─────────────────────────────────────────────────────────
# Database Table Creation on Startup
# ─────────────────────────────────────────────────────────


@app.on_event("startup")
def on_startup():
    """Create database tables on application startup."""
    Base.metadata.create_all(bind=engine)


# ─────────────────────────────────────────────────────────
# Root Endpoint
# ─────────────────────────────────────────────────────────


@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
    description="Welcome endpoint showing API information."
)
def root():
    """Root endpoint with API information."""
    return {
        "application": "device_systems API",
        "version": "3.0.0",
        "description": "API REST segura para gestión de usuarios, dispositivos y préstamos",
        "documentation": "/docs",
        "endpoints": {
            "auth": "/auth",
            "users": "/users",
            "devices": "/devices",
            "loans": "/loans"
        }
    }
