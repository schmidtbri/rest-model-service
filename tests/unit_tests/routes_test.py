import os
from pathlib import Path

import unittest
from unittest.mock import Mock
import json
from starlette.testclient import TestClient
from ml_base.utilities import ModelManager
from ml_base.ml_model import MLModelSchemaValidationException

os.chdir(Path(__file__).resolve().parent.parent.parent)

from rest_model_service.main import create_app
from rest_model_service.configuration import Model


class RoutesTests(unittest.TestCase):

    def tearDown(self) -> None:
        model_manager = ModelManager()
        model_manager.clear_instance()

    def test_root(self):
        # arrange
        app = create_app("REST Model Service", [Model(qualified_name="iris_model",
                                                      class_path="tests.mocks.IrisModel",
                                                      create_endpoint=True)])

        client = TestClient(app)

        # act
        response = client.get("/")

        # assert
        self.assertTrue(response.status_code == 200)

    def test_get_models(self):
        # arrange
        app = create_app("REST Model Service", [Model(qualified_name="iris_model",
                                                      class_path="tests.mocks.IrisModel",
                                                      create_endpoint=True)])

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

    def test_get_models_with_exception(self):
        # arrange
        app = create_app("REST Model Service", [Model(qualified_name="iris_model",
                                                      class_path="tests.mocks.IrisModel",
                                                      create_endpoint=True)])

        client = TestClient(app)

        model_manager = ModelManager()
        model_manager.get_models = Mock(side_effect=Exception("Exception!"))

        # act
        response = client.get("/api/models")

        # assert
        self.assertTrue(response.status_code == 500)
        self.assertTrue(response.json() == {
            "type": "ServiceError",
            "messages": ["Exception!"]
        })

    def test_prediction(self):
        # arrange
        app = create_app("REST Model Service", [Model(qualified_name="iris_model",
                                                      class_path="tests.mocks.IrisModel",
                                                      create_endpoint=True)])

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

    def test_prediction_with_validation_exception_raised_in_model_predict_method(self):
        # arrange
        app = create_app("REST Model Service", [Model(qualified_name="iris_model",
                                                      class_path="tests.mocks.IrisModel",
                                                      create_endpoint=True)])

        client = TestClient(app)

        model_manager = ModelManager()
        model = model_manager.get_model("iris_model")
        model.predict = Mock(side_effect=MLModelSchemaValidationException("Exception!"))

        # act
        response = client.post("/api/models/iris_model/prediction", data=json.dumps({
            "sepal_length": 6.0,
            "sepal_width": 5.0,
            "petal_length": 3.0,
            "petal_width": 2.0
        }))

        # assert
        self.assertTrue(response.status_code == 400)
        self.assertTrue(response.json() == {
            "type": "SchemaValidationError",
            "messages": ["Exception!"]
        })

    def test_prediction_with_exception_raised_in_model_predict_method(self):
        # arrange
        app = create_app("REST Model Service", [Model(qualified_name="iris_model",
                                                      class_path="tests.mocks.IrisModel",
                                                      create_endpoint=True)])

        client = TestClient(app)

        model_manager = ModelManager()
        model = model_manager.get_model("iris_model")
        model.predict = Mock(side_effect=Exception("Exception!"))

        # act
        response = client.post("/api/models/iris_model/prediction", data=json.dumps({
            "sepal_length": 6.0,
            "sepal_width": 5.0,
            "petal_length": 3.0,
            "petal_width": 2.0
        }))

        # assert
        self.assertTrue(response.status_code == 500)
        self.assertTrue(response.json() == {
            "type": "ServiceError",
            "messages": ["Exception!"]
        })

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
        self.assertTrue(response.status_code == 400)

    def test_prediction_with_bad_configuration(self):
        # arrange, act, assert
        with self.assertRaises(ValueError) as e:
            app = create_app("REST Model Service", [Model(qualified_name="asdf",
                                                          class_path="tests.mocks.IrisModel",
                                                          create_endpoint=True)])

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


if __name__ == '__main__':
    unittest.main()
