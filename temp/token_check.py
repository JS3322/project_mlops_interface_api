from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import Optional

app = FastAPI()

def check_token_in_cookie(request: Request):
    token = request.cookies.get("token")
    if token is None:
        raise HTTPException(status_code=401, detail="Token is missing in cookies")
    return token

@app.get("/example-endpoint")
async def example_endpoint(token: str = Depends(check_token_in_cookie)):
    # 클라이언트의 쿠키에 token 값이 있으면 엔드포인트 처리를 진행합니다.
    return {"message": "Access granted", "token": token}

@app.get("/another-endpoint")
async def another_endpoint(token: str = Depends(check_token_in_cookie)):
    # 이 엔드포인트에서도 동일한 쿠키 체크가 적용됩니다.
    return {"message": "Another access granted", "token": token}

# 모든 엔드포인트에 동일한 쿠키 검사를 적용하고 싶다면 각 엔드포인트에서 `Depends(check_token_in_cookie)`를 사용하십시오.