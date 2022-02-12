from pydantic import BaseModel, Field, create_model
from enum import Enum
from uuid import UUID, uuid4
from typing import Optional

from ml_base.ml_model import MLModel
from ml_base.decorator import MLModelDecorator


class IrisModelInput(BaseModel):
    sepal_length: float = Field(gt=5.0, lt=8.0, description="Length of the sepal of the flower.")
    sepal_width: float = Field(gt=2.0, lt=6.0, description="Width of the sepal of the flower.")
    petal_length: float = Field(gt=1.0, lt=6.8, description="Length of the petal of the flower.")
    petal_width: float = Field(gt=0.0, lt=3.0, description="Width of the petal of the flower.")


class Species(str, Enum):
    iris_setosa = "Iris setosa"
    iris_versicolor = "Iris versicolor"
    iris_virginica = "Iris virginica"


class IrisModelOutput(BaseModel):
    species: Species = Field(description="Predicted species of the flower.")


# creating an MLModel class to test with
class IrisModel(MLModel):
    # accessing the package metadata
    display_name = "Iris Model"
    qualified_name = "iris_model"
    description = "Model for predicting the species of a flower based on its measurements."
    version = "1.0.0"
    input_schema = IrisModelInput
    output_schema = IrisModelOutput

    def __init__(self):
        pass

    def predict(self, data):
        return IrisModelOutput(species="Iris setosa")


# creating a mockup class to test with
class SomeClass(object):
    pass


class PredictionIDDecorator(MLModelDecorator):
    """Decorator that modifies the input and output schemas of the model object."""

    @property
    def input_schema(self):
        input_schema = self._model.input_schema
        new_input_schema = create_model(
            input_schema.__name__,
            prediction_id=(Optional[str], None),
            __base__=input_schema,
        )
        return new_input_schema

    @property
    def output_schema(self):
        output_schema = self._model.output_schema
        new_output_schema = create_model(
            output_schema.__name__,
            prediction_id=(str, ...),
            __base__=output_schema,
        )
        return new_output_schema

    def predict(self, data):
        if data.prediction_id is not None:
            prediction_id = data.prediction_id
        else:
            prediction_id = str(uuid4())

        prediction = self._model.predict(data=data)
        wrapped_prediction = self.output_schema(prediction_id=prediction_id, **prediction.dict())
        return wrapped_prediction
