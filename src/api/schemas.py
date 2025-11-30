from pydantic import BaseModel, Field


class SeriveStatus(BaseModel):
    """Model representing the status of an individual service."""

    name: str = Field(..., description="Name of the service")
    status: str = Field(..., description="Current status of the service")
    details: str | None = Field(None, description="Additional details about the service status")


class HealthCheckResponse(BaseModel):
    """Model representing the health check response of the application."""

    status: str = Field(..., description="The status of the application")
    uptime: float = Field(..., description="Uptime of the application in seconds")
    services: list[SeriveStatus] = Field(
        default_factory=list, description="List of service statuses"
    )
    timestamp: float = Field(..., description="Timestamp of the health check")
