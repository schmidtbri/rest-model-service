# REST Model Service

RESTful service for hosting machine learning models.

## Installation

The package can be installed from pypi:

```bash
pip install rest_model_service
```

To use the service you must first have a working model class that uses the MLModel base class from the 
[ml_base package](https://schmidtbri.github.io/ml-base/).

You can then set up a configuration file that points at the model class, the configuration file should look like this:

```yaml
service_title: REST Model Service
models:
  - qualified_name: iris_model
    class_path: tests.mocks.IrisModel
    create_endpoint: true
```

The config file should be YAML and be in the current working directory.

The qualified name of your model and the class path to your model class should be placed in the correct place in the 
configuration file. The create_endpoint option is there for cases when you might want to load a model but not create
an endpoint for it.

## Creating an OpenAPI Contract

An OpenAPI contract can be generated dynamically for your models as hosted within the REST model service. To create 
the contract and save it execute this command:

```bash
generate_openapi --output_file=example.yaml
```

The script should be able to find your configuration file, but if you did not place it in the current working directory
you can point the script to the right path by setting an environment variable like this:

```bash
export REST_CONFIG=examples/rest_config.yaml
generate_openapi --output_file=example.yaml
```

An example rest_config.yaml file is provided in the examples of the project. It points at a model class in the tests
package.

The OpenAPI contract should be in your current working directory.

If you get an error that says something about not being able to find a module, you might need to update your 
PYTHONPATH environment variable:

```bash
export PYTHONPATH=./
```

The service relies on being able to find the model class in the python environment to load it and instantiate it. 
If your python interpreter is not able to find the model class, then the script won't be able to create an OpenAPI
contract for it. 

## Running the Service

To start the service in development mode, execute this command:

```bash
uvicorn rest_model_service.main:app --reload
```

The service should be able to find your configuration file, but if you did not place it in the current working 
directory you can point the service to the right path like this:

```bash
export REST_CONFIG='examples/rest_config.yaml'
uvicorn rest_model_service.main:app --reload
```

## Downloading Code and Setting Up for Development 

To download the code and set up a development environment use these instructions. 

To download the source code execute this command:

```bash
git clone https://github.com/schmidtbri/rest-model-service
```

Then create a virtual environment and activate it:

```bash
cd rest-model-service

make venv

# on Macs
source venv/bin/activate
```

Install the dependencies:

```bash
make dependencies
```

## Running the Unit Tests

To run the unit test suite execute these commands:

```bash
# first install the test dependencies
make test-dependencies

# run the test suite
make test

# clean up the unit tests
make clean-test
```
