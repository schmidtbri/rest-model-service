import os
from pathlib import Path

import unittest
from ml_base.utilities import ModelManager


os.chdir(Path(__file__).resolve().parent.parent.parent)

from rest_model_service.helpers import create_app
from rest_model_service.configuration import ServiceConfiguration
from rest_model_service.configuration import Model, ModelDecorator
from tests.mocks import IrisModel, PredictionIDDecorator


class MainTests(unittest.TestCase):

    def setUp(self) -> None:
        model_manager = ModelManager()
        model_manager.clear_instance()

    def tearDown(self) -> None:
        model_manager = ModelManager()
        model_manager.clear_instance()

    def test_service_info_from_configuration(self):
        # arrange, act
        configuration = ServiceConfiguration(models=[])
        app = create_app(configuration, wait_for_model_creation=True)

        # assert
        self.assertTrue(app.title == "RESTful Model Service")
        self.assertTrue(app.version == "0.1.0")
        self.assertTrue(app.description == "")

        # arrange, act
        configuration = ServiceConfiguration(service_title="asdf", version="qwe", description="asdf", models=[])
        app = create_app(configuration, wait_for_model_creation=True)

        # assert
        self.assertTrue(app.title == "asdf")
        self.assertTrue(app.version == "qwe")
        self.assertTrue(app.description == "asdf")

    def test_add_model_from_configuration(self):
        # arrange
        configuration = ServiceConfiguration(service_title="REST Model Service",
                                             models=[Model(class_path="tests.mocks.IrisModel",
                                                           create_endpoint=True)])

        app = create_app(configuration, wait_for_model_creation=True)

        model_manager = ModelManager()

        # act
        model = model_manager.get_model("iris_model")

        # assert
        self.assertTrue(type(model) is IrisModel)
        self.assertTrue(str(model) == "IrisModel")

    def test_add_model_from_configuration_with_keyword_arguments(self):
        # arrange
        configuration = ServiceConfiguration(service_title="REST Model Service",
                                             models=[Model(class_path="tests.mocks.IrisModelWithConfiguration",
                                                           create_endpoint=True,
                                                           configuration={
                                                               "option1": 123,
                                                               "option2": "asdf",
                                                               "option3": True
                                                           })])

        app = create_app(configuration, wait_for_model_creation=True)

        model_manager = ModelManager()

        # act
        model = model_manager.get_model("iris_model_with_configuration")

        # assert
        self.assertTrue(model.config["option1"] == 123)
        self.assertTrue(model.config["option2"] == "asdf")
        self.assertTrue(model.config["option3"] is True)

    def test_add_decorator_from_configuration_file_without_configuration(self):
        # arrange
        configuration = ServiceConfiguration(service_title="REST Model Service",
                                             models=[Model(class_path="tests.mocks.IrisModel",
                                                           create_endpoint=True,
                                                           decorators=[ModelDecorator(
                                                               class_path="tests.mocks.PredictionIDDecorator"
                                                           )])])

        app = create_app(configuration, wait_for_model_creation=True)

        model_manager = ModelManager()

        # act
        model = model_manager.get_model("iris_model")

        # assert
        self.assertTrue(type(model) is PredictionIDDecorator)
        self.assertTrue(str(model) == "PredictionIDDecorator(IrisModel)")

    def test_add_decorator_from_configuration_file_with_kwargs(self):
        # arrange
        configuration = ServiceConfiguration(service_title="REST Model Service",
                                             models=[Model(class_path="tests.mocks.IrisModel",
                                                           create_endpoint=True,
                                                           decorators=[
                                                               ModelDecorator(
                                                                   class_path="tests.mocks.PredictionIDDecorator",
                                                                   configuration={"asdf": "asdf", "qwer": 1}
                                                               )
                                                           ])])

        app = create_app(configuration, wait_for_model_creation=True)

        # act
        model_manager = ModelManager()
        model = model_manager.get_model("iris_model")

        # assert
        self.assertTrue(type(model) is PredictionIDDecorator)
        self.assertTrue(str(model) == "PredictionIDDecorator(IrisModel)")
        self.assertTrue(model._configuration == {"asdf": "asdf", "qwer": 1})


if __name__ == '__main__':
    unittest.main()
