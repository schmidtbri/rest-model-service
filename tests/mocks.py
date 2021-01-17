from pydantic import BaseModel, Field
from pydantic import ValidationError
from enum import Enum

from ml_base.ml_model import MLModel, MLModelSchemaValidationException


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
