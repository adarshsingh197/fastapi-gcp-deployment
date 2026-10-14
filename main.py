"""Minimal FastAPI service for Cloud Run."""

from fastapi import FastAPI

app = FastAPI(title="FastAPI on Cloud Run", version="1.0.0")


@app.get("/")
async def root() -> dict[str, str]:
    """Return a welcome message."""
    return {"message": "Welcome to the FastAPI application!"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Report that the application is running."""
    return {"status": "healthy"}


@app.get("/users/{user_id}")
async def get_user(user_id: int) -> dict[str, int]:
    """Return the requested user ID (example endpoint)."""
    return {"user_id": user_id}
