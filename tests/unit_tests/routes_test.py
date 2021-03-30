import os
from pathlib import Path

import unittest
import json
from starlette.testclient import TestClient
from ml_base.utilities import ModelManager

os.chdir(Path(__file__).resolve().parent.parent.parent)
os.environ["REST_CONFIG"] = "examples/rest_config.yaml"

from rest_model_service.main import app, create_app
from rest_model_service.configuration import Model


class RoutesTests(unittest.TestCase):

    def test_root(self):
        # arrange
        client = TestClient(app)

        # act
        response = client.get("/")

        # assert
        self.assertTrue(response.status_code == 200)

        # cleanup
        model_manager = ModelManager()
        model_manager.clear_instance()

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

        # cleanup
        model_manager = ModelManager()
        model_manager.clear_instance()

    def test_prediction(self):
        # arrange
        client = TestClient(app)

        # act
        response = client.post("/api/models/iris_model/prediction", data=json.dumps({
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

        # cleanup
        model_manager = ModelManager()
        model_manager.clear_instance()

    def test_prediction_with_bad_data(self):
        # arrange
        app = create_app("REST Model Service", [Model(qualified_name="iris_model",
                                                      class_path="tests.mocks.IrisModel",
                                                      create_endpoint=True)])

        client = TestClient(app)

        # act
        response = client.post("/api/models/iris_model/prediction", data=json.dumps({
            "sepal_length": 16.0,
            "sepal_width": 5.0,
            "petal_length": 3.0,
            "petal_width": 2.0
        }))

        # assert
        self.assertTrue(response.status_code == 422)

        # cleanup
        model_manager = ModelManager()
        model_manager.clear_instance()

    def test_prediction_with_bad_configuration(self):
        # arrange, act, assert
        with self.assertRaises(ValueError) as e:
            app = create_app("REST Model Service", [Model(qualified_name="asdf",
                                                          class_path="tests.mocks.IrisModel",
                                                          create_endpoint=True)])

        # cleanup
        model_manager = ModelManager()
        model_manager.clear_instance()

    def test_prediction_with_no_endpoint(self):
        # arrange
        app = create_app("REST Model Service", [Model(qualified_name="iris_model",
                                                      class_path="tests.mocks.IrisModel",
                                                      create_endpoint=False)])

        client = TestClient(app)

        # act
        response = client.post("/api/models/iris_model/prediction", data=json.dumps({
            "sepal_length": 16.0,
            "sepal_width": 5.0,
            "petal_length": 3.0,
            "petal_width": 2.0
        }))

        # assert
        self.assertTrue(response.status_code == 404)

        # cleanup
        model_manager = ModelManager()
        model_manager.clear_instance()


if __name__ == '__main__':
    unittest.main()
