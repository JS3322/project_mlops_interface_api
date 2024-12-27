# main.py
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from typing import List

from vo import ModelVO

app = FastAPI()
templates = Jinja2Templates(directory="templates")

fake_db = [
    {
        "model_name": "ModelA",
        "model_activation": False,
        "last_execution_time": "2024-01-01 10:00:00",
        "pid": 1111,
        "description": "첫 번째 모델 설명"
    },
    {
        "model_name": "ModelB",
        "model_activation": True,
        "last_execution_time": "2024-01-02 14:20:00",
        "pid": 2222,
        "description": "두 번째 모델 설명"
    },
    {
        "model_name": "ModelC",
        "model_activation": False,
        "last_execution_time": "2024-01-03 09:15:00",
        "pid": 3333,
        "description": "세 번째 모델 설명"
    },
]

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "table_data": fake_db
        }
    )

@app.get("/api/data", response_model=List[ModelVO])
def get_data():
    return fake_db

@app.post("/api/activate/{pid}")
def activate_model(pid: int):
    for row in fake_db:
        if row["pid"] == pid:
            row["model_activation"] = True
            return {"message": f"Model with pid={pid} activated."}
    return JSONResponse(status_code=404, content={"error": "No such model."})

@app.post("/api/deactivate/{pid}")
def deactivate_model(pid: int):
    for row in fake_db:
        if row["pid"] == pid:
            row["model_activation"] = False
            return {"message": f"Model with pid={pid} deactivated."}
    return JSONResponse(status_code=404, content={"error": "No such model."})