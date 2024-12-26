# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from typing import List
from vo import MyVO

app = FastAPI()

# Jinja2 템플릿 디렉터리 설정
templates = Jinja2Templates(directory="templates")

# 간단한 인메모리 데이터베이스 대용
fake_db = [
    {"id": 1, "value": "Hello"},
    {"id": 2, "value": "World"},
]

@app.get("/")
def index(request: Request):
    """
    Jinja 템플릿으로 메인 페이지 렌더링
    """
    # 초기 데이터도 함께 넘겨서 페이지가 뜨자마자 테이블이 채워지도록 함
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "table_data": fake_db  # Jinja에서 사용
        }
    )

@app.get("/api/data", response_model=List[MyVO])
def get_data():
    """
    테이블 데이터를 JSON 형태로 반환 (AJAX 요청용)
    """
    return fake_db

@app.post("/api/data")
def post_data(vo: MyVO):
    """
    VO 형태의 데이터를 받아서 fake_db에 추가 (테스트용)
    """
    new_item = vo.dict()
    fake_db.append(new_item)
    return {"message": "Data added", "data": new_item}