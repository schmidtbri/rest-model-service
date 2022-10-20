"""Health status manager that holds health status information for the application."""
from rest_model_service.schemas import HealthStatus, ReadinessStatus, StartupStatus


class StatusManager(object):
    """Health status manager singleton."""

    def __new__(cls, *args, **kwargs):  # noqa: D102
        """Create and return a new StatusManager instance, after instance is first created it will always be
        returned."""
        if not hasattr(cls, "_instance"):
            cls._instance = super(StatusManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._is_initialized = False
        return cls._instance

    def __init__(self):
        """Construct StatusManager object."""
        if not self._is_initialized:  # pytype: disable=attribute-error
            self._health_status = HealthStatus.UNKNOWN
            self._readiness_status = ReadinessStatus.UNKNOWN
            self._startup_status = StartupStatus.UNKNOWN
            self._is_initialized = True

    @classmethod
    def clear_instance(cls):
        """Clear singleton instance from class."""
        if hasattr(cls, "_instance"):
            del cls._instance

    def set_health_status(self, health_status: HealthStatus):
        """Set health status of the service."""
        self._health_status = health_status

    def get_health_status(self):
        """Get health status of the service."""
        return self._health_status

    def set_readiness_status(self, readiness_status: ReadinessStatus):
        """Set readiness status of the service."""
        self._readiness_status = readiness_status

    def get_readiness_status(self):
        """Get readiness status of the service."""
        return self._readiness_status

    def set_startup_status(self, startup_status: StartupStatus):
        """Set startup status of the service."""
        self._startup_status = startup_status

    def get_startup_status(self):
        """Get startup status of the service."""
        return self._startup_status
