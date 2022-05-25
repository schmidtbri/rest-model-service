![Code Quality Status](https://github.com/schmidtbri/rest-model-service/actions/workflows/test.yml/badge.svg)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-green)](https://opensource.org/licenses/BSD-3-Clause)
[![PyPi](https://img.shields.io/badge/pypi-v0.3.0-green)](https://pypi.org/project/rest-model-service/)

# rest-model-service

**rest-model-service** is a package for building RESTful services for hosting machine learning models.

## Installation

The package can be installed from pypi:

```bash
pip install rest_model_service
```

## Usage 

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

### Adding a Decorator to a Model

The rest_model_service package also supports decorators as defined in the ml_base package and explained 
[here](https://schmidtbri.github.io/ml-base/decorator/). A decorator can be added to a model by adding the "decorators" 
key to the model's configuration:

```yaml
service_title: REST Model Service With Decorators
models:
  - qualified_name: iris_model
    class_path: tests.mocks.IrisModel
    create_endpoint: true
    decorators:
      - class_path: tests.mocks.PredictionIDDecorator
```

The PredictionIDDecorator will be instantiated and added to the IrisModel instance at application startup. Parameters
can also be provided to the decorator's `__init__()` method like this:

```yaml
service_title: REST Model Service With Decorators
models:
  - qualified_name: iris_model
    class_path: tests.mocks.IrisModel
    create_endpoint: true
    decorators:
      - class_path: tests.mocks.PredictionIDDecorator
        configuration:
          parameter1: "asdf"
          parameter2: "zxcv"
```

The configuration dictionary will be passed to the decorator as keyword arguments.

### Adding Logging Configuration

The service also optionally accepts logging configuration through the YAML configuration file:

```yaml
service_title: REST Model Service With Logging
models:
  - qualified_name: iris_model
    class_path: tests.mocks.IrisModel
    create_endpoint: true
logging:
    version: 1
    disable_existing_loggers: true
    formatters:
      formatter:
        class: logging.Formatter
        format: "%(asctime)s %(pathname)s %(lineno)s %(levelname)s %(message)s"
    handlers:
      stdout:
        level: INFO
        class: logging.StreamHandler
        stream: ext://sys.stdout
        formatter: formatter
    loggers:
      root:
        level: INFO
        handlers:
        - stdout
        propagate: false
```

The YAML needs to be formatted so that it deserializes to a dictionary that matches the logging package's [configuration
dictionary schema](https://docs.python.org/3/library/logging.config.html#logging-config-dictschema).

### Creating an OpenAPI Contract

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

### Running the Service

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

## Development

Download the source code with this command:

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

## Testing

To run the unit test suite execute these commands:

```bash
# first install the test dependencies
make test-dependencies

# run the test suite
make test

# clean up the unit tests
make clean-test
```
