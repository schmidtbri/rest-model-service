import os
from pathlib import Path

import unittest
from ml_base.utilities import ModelManager


os.chdir(Path(__file__).resolve().parent.parent.parent)

from rest_model_service.main import create_app
from rest_model_service.configuration import Model, ModelDecorator
from tests.mocks import IrisModel, PredictionIDDecorator


class MainTests(unittest.TestCase):

    def setUp(self) -> None:
        model_manager = ModelManager()
        model_manager.clear_instance()

    def tearDown(self) -> None:
        model_manager = ModelManager()
        model_manager.clear_instance()

    def test_title_configuration(self):
        # arrange, act
        app = create_app("REST Model Service", [])

        # assert
        self.assertTrue(app.title == "REST Model Service")

    def test_add_model_from_configuration(self):
        # arrange
        app = create_app("REST Model Service", [Model(qualified_name="iris_model",
                                                      class_path="tests.mocks.IrisModel",
                                                      create_endpoint=True)])

        model_manager = ModelManager()

        # act
        model = model_manager.get_model("iris_model")

        # assert
        self.assertTrue(type(model) is IrisModel)
        self.assertTrue(str(model) == "IrisModel")

    def test_add_decorator_from_configuration_file_without_configuration(self):
        # arrange
        app = create_app("REST Model Service", [Model(qualified_name="iris_model",
                                                      class_path="tests.mocks.IrisModel",
                                                      create_endpoint=True,
                                                      decorators=[ModelDecorator(
                                                          class_path="tests.mocks.PredictionIDDecorator"
                                                      )])])

        model_manager = ModelManager()

        # act
        model = model_manager.get_model("iris_model")

        # assert
        self.assertTrue(type(model) is PredictionIDDecorator)
        self.assertTrue(str(model) == "PredictionIDDecorator(IrisModel)")

    def test_add_decorator_from_configuration_file_with_configuration(self):
        # arrange
        app = create_app("REST Model Service", [Model(qualified_name="iris_model",
                                                      class_path="tests.mocks.IrisModel",
                                                      create_endpoint=True,
                                                      decorators=[
                                                          ModelDecorator(
                                                              class_path="tests.mocks.PredictionIDDecorator",
                                                              configuration={"asdf": "asdf", "qwer": 1}
                                                          )
                                                      ])])

        # act
        model_manager = ModelManager()
        model = model_manager.get_model("iris_model")

        # assert
        self.assertTrue(type(model) is PredictionIDDecorator)
        self.assertTrue(str(model) == "PredictionIDDecorator(IrisModel)")
        self.assertTrue(model._configuration == {"asdf": "asdf", "qwer": 1})


if __name__ == '__main__':
    unittest.main()
