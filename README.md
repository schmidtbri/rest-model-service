![Code Quality Status](https://github.com/schmidtbri/rest-model-service/actions/workflows/test.yml/badge.svg)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-green)](https://opensource.org/licenses/BSD-3-Clause)
[![PyPi](https://img.shields.io/badge/pypi-v0.4.0-green)](https://pypi.org/project/rest-model-service/)

# rest-model-service

**rest-model-service** is a package for building RESTful services for hosting machine learning models.

## Installation

The package can be installed from pypi:

```bash
pip install rest_model_service
```

## Usage 

To use the service you must first have a working model class that uses the MLModel base class from the 
[ml_base package](https://schmidtbri.github.io/ml-base/). The MLModel base class is designed to provide a consistent 
interface around model prediction logic that allows the rest_model_service package to deploy any model that implements 
it. Some examples of how to create MLModel classes for your model can be found 
[here](https://schmidtbri.github.io/ml-base/basic/).

You can then set up a configuration file that points at the model class. The configuration file should look 
like this:

```yaml
service_title: "REST Model Service"
models:
  - qualified_name: iris_model
    class_path: tests.mocks.IrisModel
    create_endpoint: true
```

The qualified name of your model and the class path to your model class should be placed in the correct place in the 
configuration file. The "create_endpoint" option is there for cases when you might want to load a model but not create
an endpoint for it, if it is set to "false" the model will be loaded and available for use within the service but
will not have an endpoint defined for it.

The config file should be YAML, be named "rest_config.yaml", and be in the current working directory. However, 
we can point at configuration files that are in different locations if needed.

The service can host many models, all that is needed is to add entries to the "models" array.

### Adding Service Information

We can add several details to the configuration file that are useful when building OpenAPI specifications. 

```yaml
service_title: "REST Model Service"
description: "Service description"
version: "1.1.0"
models:
  - qualified_name: iris_model
    class_path: tests.mocks.IrisModel
    create_endpoint: true
```

The service title, description, and version are passed into the application and used to build the OpenAPI specification.
Details for how to build the OpenAPI document for your model service are below.

### Adding a Decorator to a Model

The rest_model_service package also supports the [decorator pattern](https://en.wikipedia.org/wiki/Decorator_pattern). 
Decorators are defined in the [ml_base package](https://schmidtbri.github.io/ml-base/) and explained
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

The PredictionIDDecorator will be instantiated and added to the IrisModel instance when the service starts up. 
Keyword arguments can also be provided to the decorator's `__init__()` by adding a "configuration" key to the 
decorator's entry like this:

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

The configuration dictionary will be passed to the decorator class as keyword arguments.

Many decorators can be added to a single model, each decorator will decorate the decorator that was previously attached 
to the model. This will create a "stack" of decorators that will handle the prediction request before the model's 
prediction is created.

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
generate_openapi
```

The command looks for a "rest_config.yaml" in the current working directory and creates the application from it.
The command then saves the resulting OpenAPI document to a file named "openapi.yaml" in the current working directory.

You can provide a path to the configuration file like this:

```bash
generate_openapi --configuration_file=examples/rest_config.yaml
```

You can also provide the desired path for the OpenAPI document like this:

```bash
generate_openapi --output_file=example.yaml
```

Both options together:

```bash
generate_openapi --configuration_file=examples/rest_config.yaml --output_file=example.yaml
```

An example rest_config.yaml file is provided in the examples of the project. It points at a MLModel class in the tests
package.

### Common Errors

If you get an error that says something about not being able to find a module, you might need to update your 
PYTHONPATH environment variable:

```bash
export PYTHONPATH=./
```

The service relies on being able to find the model classes and the decorator classes in the python environment to load 
them and instantiate them. If your Python interpreter is not able to find the classes, then the service won't be able
to instantiate the model classes or create endpoints for the models or an OpenAPI document for them. 

### Using Status Check Endpoints

The service supports three status check endpoints:

- "/api/health", indicates whether the service process is running. This endpoint will return a 200 status once the 
  service has started.
- "/api/health/ready", indicates whether the service is ready to respond to requests. This endpoint will return a 200 
  status only if all the models and decorators have finished being instantiated without errors. Once the models and 
  decorators are loaded, the readiness check will always return a ACCEPTING_TRAFFIC state.
- "/api/health/startup", indicates whether the service is started. This endpoint will return a 200 status only if all 
  the models and decorators have finished being instantiated without errors.

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

cd rest-model-service
```

Then create a virtual environment and activate it:

```bash
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
