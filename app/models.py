"""Pydantic models used by the FastAPI application.

This module defines the request/response models used across the app.
"""

from typing import Optional
from pydantic import BaseModel, Field


""" Todo Base Class """


class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: bool = False


""" TodoCreate Class """


class TodoCreate(TodoBase):
    pass


""" TodoUpdate Class """


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = False


""" Todo Class """


class Todo(TodoBase):
    """Represents a todo item stored or returned by the API."""

    id: int

    class ConfigDict:
        from_attributes = True


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str


class JenkinsResponse(BaseModel):
    """Response model for jenkins"""

    status: str
