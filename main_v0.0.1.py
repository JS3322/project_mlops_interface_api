from fastapi import FastAPI
from src.mlops.application import ExecuteExampleApplication

import uvicorn

app = FastAPI()

app.include_router(ExecuteExampleApplication.router, prefix="/v1/autotdk/publish/execute")

if __name__ == "__main__"
	uvicorn.run(app, host="0.0.0.0", port=8000)
