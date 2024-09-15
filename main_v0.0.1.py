from fastapi import FastAPI
from src.common.middleware.example import add_process_time_header
from src.ml.application import execute_example_application

import uvicorn

app = FastAPI()
app.middleware("http")(add_process_time_header)
app.include_router(execute_example_application.route, prefix="/v1/ml/request")

if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)
