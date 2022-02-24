import unittest
import os
from os.path import dirname, abspath, join


class InitTests(unittest.TestCase):

    def test_version_available(self):
        # arrange, put a version.txt file in place
        root = abspath(dirname(dirname(dirname(__file__))))
        with open(join(root, "rest_model_service", "version.txt"), "w") as f:
            f.write("0.1.0")

        # act
        import rest_model_service
        import importlib
        importlib.reload(rest_model_service)

        # assert

        self.assertTrue(rest_model_service.__version__ == "0.1.0")

        # tear down
        os.remove(join(root, "rest_model_service", "version.txt"))

    def test_version_not_available(self):
        # arrange, act
        import rest_model_service
        import importlib
        importlib.reload(rest_model_service)

        # assert
        self.assertTrue(rest_model_service.__version__ == "N/A")


if __name__ == "__main__":
    unittest.main()
