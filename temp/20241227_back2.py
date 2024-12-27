# main.py
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from typing import List

from vo import ModelVO

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# 간단한 인메모리 DB 대용
# 실제로는 DB 연결하여 관리하는 것이 바람직함.
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
    """
    Jinja 템플릿으로 메인 페이지 렌더링.
    테이블에 표시할 데이터(fake_db)를 함께 전달.
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "table_data": fake_db
        }
    )

@app.get("/api/data", response_model=List[ModelVO])
def get_data():
    """
    AJAX를 통해 테이블 데이터를 요청할 때 호출.
    ModelVO 리스트 형태로 JSON 반환.
    """
    return fake_db

@app.post("/api/activate/{pid}")
def activate_model(pid: int):
    """
    모델 활성화 요청 API.
    - pid에 해당하는 row의 model_activation을 True로 변경.
    """
    updated = False
    for row in fake_db:
        if row["pid"] == pid:
            row["model_activation"] = True
            updated = True
            break
    if updated:
        return {"message": f"Model with pid={pid} is now activated."}
    else:
        return JSONResponse(status_code=404, content={"error": "No such model pid."})