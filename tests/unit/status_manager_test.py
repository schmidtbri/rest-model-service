import unittest

from rest_model_service.status_manager import StatusManager
from rest_model_service.schemas import HealthStatus, ReadinessStatus, StartupStatus


class StatusManagerTests(unittest.TestCase):

    def test_status_manager_will_return_same_instance_when_instantiated_many_times(self):
        # arrange, act
        # instantiating the model manager class twice
        first_status_manager = StatusManager()
        second_status_manager = StatusManager()

        # assert
        self.assertTrue(id(first_status_manager) == id(second_status_manager))

        # cleanup
        first_status_manager.clear_instance()

    def test_status_manager_will_not_execute_init_twice(self):
        # arrange
        # instantiating the model manager class twice
        first_status_manager = StatusManager()
        first_status_manager.set_health_status(HealthStatus.NOT_HEALTHY)

        # act
        second_status_manager = StatusManager()

        # assert
        self.assertTrue(first_status_manager._health_status != HealthStatus.HEALTHY)

        # cleanup
        first_status_manager.clear_instance()

    def test_status_manager_returns_correct_statuses_when_first_instantiated(self):
        # arrange
        StatusManager.clear_instance()
        status_manager = StatusManager()

        # act
        health_status = status_manager.get_health_status()
        readiness_status = status_manager.get_readiness_status()
        startup_status = status_manager.get_startup_status()

        # assert
        self.assertTrue(health_status == HealthStatus.UNKNOWN)
        self.assertTrue(readiness_status == ReadinessStatus.UNKNOWN)
        self.assertTrue(startup_status == StartupStatus.UNKNOWN)

    def test_status_manager_state_is_shared_across_many_instances(self):
        # arrange, act
        first_status_manager = StatusManager()
        second_status_manager = StatusManager()

        # assert
        self.assertTrue(first_status_manager.get_startup_status() == second_status_manager.get_startup_status())
        self.assertTrue(first_status_manager.get_readiness_status() == second_status_manager.get_readiness_status())
        self.assertTrue(first_status_manager.get_startup_status() == second_status_manager.get_startup_status())

        # act
        first_status_manager.set_health_status(HealthStatus.NOT_HEALTHY)
        first_status_manager.set_readiness_status(ReadinessStatus.ACCEPTING_TRAFFIC)
        first_status_manager.set_startup_status(StartupStatus.STARTED)

        # assert
        self.assertTrue(first_status_manager.get_startup_status() == second_status_manager.get_startup_status())
        self.assertTrue(first_status_manager.get_readiness_status() == second_status_manager.get_readiness_status())
        self.assertTrue(first_status_manager.get_startup_status() == second_status_manager.get_startup_status())

        # cleanup
        first_status_manager.clear_instance()
        second_status_manager.clear_instance()


if __name__ == '__main__':
    unittest.main()
