# rest_model_service

RESTful service for hosting machine learning models.



## Running the Service

```bash
export models='["tests.mocks.IrisModel"]'
uvicorn rest_model_service.main:app --reload
```
