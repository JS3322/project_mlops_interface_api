from fastapi import FastAPI, Depends, Cookie
from src.common.middleware.example import add_process_time_header
from src.ml.application import execute_example_application

import uvicorn

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

app.middleware("http")(add_process_time_header)
app.include_router(execute_example_application.route, prefix="/v1/ml/request")

if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)
