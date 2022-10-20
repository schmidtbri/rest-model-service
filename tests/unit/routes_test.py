import os
from pathlib import Path

import unittest
from unittest.mock import Mock
import json
from starlette.testclient import TestClient
from ml_base.utilities import ModelManager
from ml_base.ml_model import MLModelSchemaValidationException

os.chdir(Path(__file__).resolve().parent.parent.parent)

from rest_model_service.helpers import create_app
from rest_model_service.configuration import Configuration, Model


class RoutesTests(unittest.TestCase):

    def tearDown(self) -> None:
        model_manager = ModelManager()
        model_manager.clear_instance()

    def test_root(self):
        # arrange
        configuration = Configuration(models=[Model(qualified_name="iris_model",
                                                    class_path="tests.mocks.IrisModel",
                                                    create_endpoint=True)])

        app = create_app(configuration, wait_for_model_creation=True)

        # act
        with TestClient(app) as client:
            response = client.get("/")

            # assert
            self.assertTrue(response.status_code == 200)

    def test_get_models(self):
        # arrange
        configuration = Configuration(models=[Model(qualified_name="iris_model",
                                                    class_path="tests.mocks.IrisModel",
                                                    create_endpoint=True)])

        app = create_app(configuration, wait_for_model_creation=True)

        # act
        with TestClient(app) as client:
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

    def test_get_model_metadata(self):
        # arrange
        configuration = Configuration(models=[Model(qualified_name="iris_model",
                                                    class_path="tests.mocks.IrisModel",
                                                    create_endpoint=True)])

        app = create_app(configuration, wait_for_model_creation=True)

        # act
        with TestClient(app) as client:
            response = client.get("/api/models/iris_model/metadata")

            # assert
            self.assertTrue(response.status_code == 200)
            self.assertTrue(response.json() == {
                'display_name': 'Iris Model',
                'qualified_name': 'iris_model',
                'description': 'Model for predicting the species of a flower based on its measurements.',
                'version': '1.0.0',
                'input_schema': {'title': 'IrisModelInput', 'type': 'object', 'properties': {'sepal_length': {'title': 'Sepal Length', 'description': 'Length of the sepal of the flower.', 'exclusiveMinimum': 5.0, 'exclusiveMaximum': 8.0, 'type': 'number'}, 'sepal_width': {'title': 'Sepal Width', 'description': 'Width of the sepal of the flower.', 'exclusiveMinimum': 2.0, 'exclusiveMaximum': 6.0, 'type': 'number'}, 'petal_length': {'title': 'Petal Length', 'description': 'Length of the petal of the flower.', 'exclusiveMinimum': 1.0, 'exclusiveMaximum': 6.8, 'type': 'number'}, 'petal_width': {'title': 'Petal Width', 'description': 'Width of the petal of the flower.', 'exclusiveMinimum': 0.0, 'exclusiveMaximum': 3.0, 'type': 'number'}}, 'required': ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']},
                'output_schema': {'title': 'IrisModelOutput', 'type': 'object', 'properties': {'species': {'description': 'Predicted species of the flower.', 'allOf': [{'$ref': '#/definitions/Species'}]}}, 'required': ['species'], 'definitions': {'Species': {'title': 'Species', 'description': 'An enumeration.', 'enum': ['Iris setosa', 'Iris versicolor', 'Iris virginica'], 'type': 'string'}}}
            })

    def test_get_models_with_exception(self):
        # arrange
        model_manager = ModelManager()
        model_manager.get_models = Mock(side_effect=Exception("Exception!"))

        configuration = Configuration(models=[Model(qualified_name="iris_model",
                                                    class_path="tests.mocks.IrisModel",
                                                    create_endpoint=True)])

        app = create_app(configuration, wait_for_model_creation=True)

        # act
        with TestClient(app) as client:
            response = client.get("/api/models")

            # assert
            self.assertTrue(response.status_code == 500)
            self.assertTrue(response.json() == {
                "type": "ServiceError",
                "messages": ["Exception!"]
            })

    def test_get_model_metadata_with_exception(self):
        # arrange
        model_manager = ModelManager()
        model_manager.get_model_metadata = Mock(side_effect=Exception("Exception!"))

        configuration = Configuration(models=[Model(qualified_name="iris_model",
                                                    class_path="tests.mocks.IrisModel",
                                                    create_endpoint=True)])

        app = create_app(configuration, wait_for_model_creation=True)

        # act
        with TestClient(app) as client:
            response = client.get("/api/models/iris_model/metadata")

            # assert
            self.assertTrue(response.status_code == 500)
            self.assertTrue(response.json() == {
                "type": "ServiceError",
                "messages": ["Exception!"]
            })

    def test_prediction(self):
        # arrange
        configuration = Configuration(models=[Model(qualified_name="iris_model",
                                                    class_path="tests.mocks.IrisModel",
                                                    create_endpoint=True)])

        app = create_app(configuration, wait_for_model_creation=True)

        # act
        with TestClient(app) as client:
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
        configuration = Configuration(models=[Model(qualified_name="iris_model",
                                                    class_path="tests.mocks.IrisModel",
                                                    create_endpoint=True)])

        app = create_app(configuration, wait_for_model_creation=True)

        model_manager = ModelManager()
        model = model_manager.get_model("iris_model")
        model.predict = Mock(side_effect=MLModelSchemaValidationException("Exception!"))

        # act
        with TestClient(app) as client:
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
        configuration = Configuration(models=[Model(qualified_name="iris_model",
                                                    class_path="tests.mocks.IrisModel",
                                                    create_endpoint=True)])

        app = create_app(configuration, wait_for_model_creation=True)

        model_manager = ModelManager()
        model = model_manager.get_model("iris_model")
        model.predict = Mock(side_effect=Exception("Exception!"))

        # act
        with TestClient(app) as client:
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
        configuration = Configuration(models=[Model(qualified_name="iris_model",
                                                    class_path="tests.mocks.IrisModel",
                                                    create_endpoint=True)])

        app = create_app(configuration, wait_for_model_creation=True)

        # act
        with TestClient(app) as client:
            response = client.post("/api/models/iris_model/prediction", data=json.dumps({
                "sepal_length": 16.0,
                "sepal_width": 5.0,
                "petal_length": 3.0,
                "petal_width": 2.0
            }))

        # assert
        self.assertTrue(response.status_code == 400)

    def test_prediction_with_no_endpoint(self):
        # arrange
        configuration = Configuration(models=[Model(qualified_name="iris_model",
                                                    class_path="tests.mocks.IrisModel",
                                                    create_endpoint=False)])

        app = create_app(configuration, wait_for_model_creation=True)

        # act
        with TestClient(app) as client:
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
