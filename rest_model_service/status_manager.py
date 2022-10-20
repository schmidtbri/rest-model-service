"""Health status manager that holds health status information for the application."""
from typing import Tuple, Dict
from rest_model_service.schemas import HealthStatus, ReadinessStatus, StartupStatus


class StatusManager(object):
    """Health status manager singleton."""

    def __new__(cls, *args: Tuple, **kwargs: Dict):  # noqa: D102, ANN101, ANN204
        """Create new StatusManager instance, after instance is first created it will always be returned."""
        if not hasattr(cls, "_instance"):
            cls._instance = super(StatusManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._is_initialized = False
        return cls._instance

    def __init__(self) -> None:  # noqa: ANN101
        """Construct StatusManager object."""
        if not self._is_initialized:  # pytype: disable=attribute-error
            self._health_status = HealthStatus.UNKNOWN
            self._readiness_status = ReadinessStatus.UNKNOWN
            self._startup_status = StartupStatus.UNKNOWN
            self._is_initialized = True

    @classmethod
    def clear_instance(cls) -> None:  # noqa: ANN102
        """Clear singleton instance from class."""
        if hasattr(cls, "_instance"):
            del cls._instance

    def set_health_status(self, health_status: HealthStatus) -> None:  # noqa: ANN101
        """Set health status of the service."""
        self._health_status = health_status

    def get_health_status(self) -> HealthStatus:  # noqa: ANN101
        """Get health status of the service."""
        return self._health_status

    def set_readiness_status(self, readiness_status: ReadinessStatus) -> None:  # noqa: ANN101
        """Set readiness status of the service."""
        self._readiness_status = readiness_status

    def get_readiness_status(self) -> ReadinessStatus:  # noqa: ANN101
        """Get readiness status of the service."""
        return self._readiness_status

    def set_startup_status(self, startup_status: StartupStatus) -> None:  # noqa: ANN101
        """Set startup status of the service."""
        self._startup_status = startup_status

    def get_startup_status(self) -> StartupStatus:  # noqa: ANN101
        """Get startup status of the service."""
        return self._startup_status
