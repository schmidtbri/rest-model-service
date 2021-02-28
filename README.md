# REST Model Service

RESTful service for hosting machine learning models.

# Installation


## Running the Service

```bash
export models='["tests.mocks.IrisModel"]'
uvicorn rest_model_service.main:app --reload
```


## Downloading and Setting Up for Development 

To download the code and set up a development environment use these instructions. 

To download the source code execute this command:

```bash
git clone https://github.com/schmidtbri/ml-base
```

Then create a virtual environment and activate it:

```bash
# go into the project directory
cd ml-base

make venv

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

