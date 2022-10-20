from os import path
from io import open
from setuptools import setup, find_packages


def load_file(file_name):
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, file_name)) as f:
        return f.read()


setup(name="rest_model_service",
      version=load_file("rest_model_service/version.txt"),
      author="Brian Schmidt",
      author_email="6666331+schmidtbri@users.noreply.github.com",
      description="RESTful service for hosting machine learning models.",
      long_description=load_file("README.md"),
      long_description_content_type="text/markdown",
      url="https://github.com/schmidtbri/rest-model-service",
      license="BSD",
      packages=find_packages(exclude=["tests", "*tests", "tests*"]),
      entry_points={
          "console_scripts": [
              "generate_openapi=rest_model_service.generate_openapi:main",
          ]
      },
      python_requires=">=3.7",
      install_requires=["ml-base>=0.2.0", "fastapi", "uvicorn", "pyyaml"],
      tests_require=["pytest", "pytest-html", "pylama", "coverage", "coverage-badge", "radon", "bandit", "safety",
                     "flake8-annotations"],
      package_data={
          "rest_model_service": [
                  "version.txt"
            ]
      },
      classifiers=[
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
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
