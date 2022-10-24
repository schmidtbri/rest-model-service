import os
from pathlib import Path
import unittest
import time
from fastapi.testclient import TestClient

os.chdir(Path(__file__).resolve().parent.parent.parent)

from rest_model_service.helpers import create_app
from rest_model_service.configuration import Model, Configuration


class AppTests(unittest.TestCase):

    def test_service_endpoints_with_no_models(self):
        # arrange
        app = create_app(Configuration(service_title="REST Model Service",
                                       models=[]))

        # act
        with TestClient(app) as client:
            response = client.get("/")
            health_response = client.get("/api/health")
            readiness_response = client.get("/api/health/ready")
            startup_status = client.get("/api/health/startup")

            # assert
            self.assertTrue(response.status_code == 200)
            self.assertTrue(health_response.status_code == 200)
            self.assertTrue(readiness_response.status_code == 200)
            self.assertTrue(startup_status.status_code == 200)

    def test_health_endpoints_with_slow_loading_model(self):
        # arrange
        configuration = Configuration(service_title="REST Model Service",
                                      models=[
                                          Model(qualified_name="slow_iris_model",
                                                class_path="tests.mocks.SlowIrisModel",
                                                create_endpoint=True)])

        app = create_app(configuration)

        with TestClient(app) as client:
            # act
            health_response = client.get("/api/health")
            readiness_response = client.get("/api/health/ready")
            startup_status = client.get("/api/health/startup")

            # assert
            # because the slow model has not finished starting up, the readiness and startup statuses are 500
            self.assertTrue(health_response.status_code == 200)
            self.assertTrue(readiness_response.status_code == 503)
            self.assertTrue(startup_status.status_code == 503)

            # waiting for the slow model to finish starting up
            time.sleep(7)

            # act
            health_response = client.get("/api/health")
            readiness_response = client.get("/api/health/ready")
            startup_status = client.get("/api/health/startup")

            # assert
            # after the slow model finishes starting up, the statuses should all be 200
            self.assertTrue(health_response.status_code == 200)
            self.assertTrue(readiness_response.status_code == 200)
            self.assertTrue(startup_status.status_code == 200)

    def test_health_endpoints_with_model_that_throws_exception_in_init(self):
        # arrange
        configuration = Configuration(service_title="REST Model Service",
                                      models=[
                                          Model(qualified_name="iris_model_with_exception",
                                                class_path="tests.mocks.IrisModelWithException",
                                                create_endpoint=True)])
        app = create_app(configuration)

        with TestClient(app) as client:
            # act
            health_response = client.get("/api/health")
            readiness_response = client.get("/api/health/ready")
            startup_status = client.get("/api/health/startup")

            # assert
            # because the slow model has not finished starting up, the readiness and startup statuses are 503
            self.assertTrue(health_response.status_code == 200)
            self.assertTrue(readiness_response.status_code == 503)
            self.assertTrue(startup_status.status_code == 503)

            # waiting for the slow model to finish starting up
            time.sleep(4)

            # act
            health_response = client.get("/api/health")
            readiness_response = client.get("/api/health/ready")
            startup_status = client.get("/api/health/startup")

            # assert
            # after the slow model finishes starting up, the statuses should all be 200
            self.assertTrue(health_response.status_code == 503)
            self.assertTrue(readiness_response.status_code == 503)
            self.assertTrue(startup_status.status_code == 200)


if __name__ == '__main__':
    unittest.main()
