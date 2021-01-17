import unittest

from rest_model_service.schemas import *


class SchemasTests(unittest.TestCase):

    def test_model_metadata_type(self):
        # arrange
        data = {
            "display_name": "test",
            "qualified_name": "test",
            "description": "test",
            "version": "1.0.0",
        }

        # act
        instance = ModelMetadata(**data)

        # assert
        self.assertTrue(type(instance) is ModelMetadata)
        self.assertTrue(instance.display_name == "test")
        self.assertTrue(instance.qualified_name == "test")
        self.assertTrue(instance.description == "test")
        self.assertTrue(instance.version == "1.0.0")

    def test_model_metadata_collection_type(self):
        # arrange
        data = {
            "models": [
                {
                    "display_name": "test",
                    "qualified_name": "test",
                    "description": "test",
                    "version": "1.0.0",
                }
            ]
        }

        # act
        instance = ModelMetadataCollection(**data)

        # assert
        self.assertTrue(type(instance) is ModelMetadataCollection)
        self.assertTrue(instance.models[0].display_name == "test")
        self.assertTrue(instance.models[0].qualified_name == "test")
        self.assertTrue(instance.models[0].description == "test")
        self.assertTrue(instance.models[0].version == "1.0.0")


if __name__ == '__main__':
    unittest.main()
