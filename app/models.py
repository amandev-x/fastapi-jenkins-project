"""Pydantic models used by the FastAPI application.

This module defines the request/response models used across the app.
"""

from typing import Optional
from pydantic import BaseModel


class Todo(BaseModel):
    """Represents a todo item stored or returned by the API."""

    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    completed: bool = False


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str
