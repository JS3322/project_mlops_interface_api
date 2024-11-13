from fastapi import FastAPI, Depends, Cookie, HTTPException
from fastapi.responses import HTMLResponse
from src.common.middleware.example import add_process_time_header
from src.ml.application import execute_example_application

import uvicorn
import os

app = FastAPI(
	title="mlops API interface",
    description="""
    Notice: engine 테스트 용도  
    """,
    version="0.1.0"
)

# 쿠키에서 SSO 토큰을 가져오는 의존성 함수
async def get_token_from_cookie(token: str = Cookie(None)):
    return token

@app.get("/token")
async def read_token(token: str = Depends(get_token_from_cookie)):
    return {"token": token}

@app.get("/intro", response_class=HTMLResponse)
async def intro_page(token: str = Depends(get_token_from_cookie), bbb: str = "dddd"):
    if token:
        # HTML 파일 경로
        file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "src/static/intro.html")
        with open(file_path, "r") as file:
            html_content = file.read()
            # bbb 값을 HTML에 삽입
            html_content = html_content.replace("{{ bbb_value }}", bbb)
            return html_content
    else:
        # 토큰이 없을 경우 500 에러 발생
        raise HTTPException(status_code=500, detail="Internal Server Error: Token not found.")

app.middleware("http")(add_process_time_header)
app.include_router(execute_example_application.route, prefix="/v1/ml/request")

if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)
