import os
import unittest
import json
from fastapi.testclient import TestClient

os.environ["models"] = '["tests.mocks.IrisModel"]'

from rest_model_service.main import app


class RoutesTests(unittest.TestCase):

    def test_root(self):
        # arrange
        client = TestClient(app)

        # act
        response = client.get("/")

        # assert
        self.assertTrue(response.status_code == 200)

    def test_get_models(self):
        # arrange
        client = TestClient(app)

        # act
        response = client.get("/api/models")

        # assert
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json() == {
            "models":
                [
                    {
                        "display_name": "Iris Model",
                        "qualified_name": "iris_model",
                        "description": "Model for predicting the species of a flower based on its measurements.",
                        "version": "1.0.0"
                    }
                ]
        })

    def test_prediction(self):
        # arrange
        client = TestClient(app)

        # act
        response = client.post("/api/models/iris_model/predict", data=json.dumps({
            "sepal_length": 6.0,
            "sepal_width": 5.0,
            "petal_length": 3.0,
            "petal_width": 2.0
        }))

        # assert
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json() == {
            "species": "Iris setosa"
        })

    def test_prediction_with_bad_data(self):
        # arrange
        client = TestClient(app)

        # act
        response = client.post("/api/models/iris_model/predict", data=json.dumps({
            "sepal_length": 16.0,
            "sepal_width": 5.0,
            "petal_length": 3.0,
            "petal_width": 2.0
        }))

        # assert
        self.assertTrue(response.status_code == 422)


if __name__ == '__main__':
    unittest.main()
