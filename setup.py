from os import path
from io import open
from setuptools import setup, find_packages

from rest_model_service import __name__, __version__, __doc__


def load_file(file_name):
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, file_name)) as f:
        return f.read()


setup(name=__name__,
      version=__version__,
      author="Brian Schmidt",
      author_email="6666331+schmidtbri@users.noreply.github.com",
      description=__doc__,
      long_description=load_file("README.md"),
      long_description_content_type="text/markdown",
      url="https://github.com/schmidtbri/rest-model-service",
      license="BSD",
      packages=find_packages(exclude=["tests", "*tests", "tests*"]),
      entry_points={
          'console_scripts': [
              'generate_openapi=rest_model_service.generate_openapi:main',
          ]
      },
      python_requires=">=3.5",
      install_requires=["ml-base", "fastapi", "uvicorn", "pyyaml"],
      tests_require=['pytest', 'pytest-html', 'pylama', 'coverage', 'coverage-badge', 'bandit', 'safety', "pytype",
                     "flake8-annotations"],
      classifiers=[
          "Programming Language :: Python :: 3",
          "Intended Audience :: Developers",
          "Operating System :: OS Independent"
      ],
      project_urls={
          "Documentation": "https://schmidtbri.github.io/rest-model-service/",
          "Source Code": "https://github.com/schmidtbri/rest-model-service",
          "Tracker": "https://github.com/schmidtbri/rest-model-service/issues"
      },
      keywords=[
          "machine learning", "REST", "service"
      ])
