from fastapi import FastAPI, HTTPException, Depends, Request
from enum import Enum
from fastapi.responses import JSONResponse

# 에러 코드 및 메시지를 Enum으로 정의합니다.
class ErrorCode(Enum):
    TOKEN_MISSING = (401, "Token is missing in cookies")
    TOKEN_INVALID = (403, "Token is invalid")

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

# 에러를 처리하는 유틸리티 함수
def raise_error(error: ErrorCode):
    raise HTTPException(status_code=error.status_code, detail=error.message)

app = FastAPI()

# 쿠키에 token 값이 있는지 체크하는 함수
def check_token_in_cookie(request: Request):
    token = request.cookies.get("token")
    if token is None:
        raise_error(ErrorCode.TOKEN_MISSING)
    # 추가적인 토큰 검증 로직이 필요하다면 여기에 추가
    # 예: if not validate_token(token): raise_error(ErrorCode.TOKEN_INVALID)
    return token

@app.get("/example-endpoint")
async def example_endpoint(token: str = Depends(check_token_in_cookie)):
    return {"message": "Access granted", "token": token}

@app.get("/another-endpoint")
async def another_endpoint(token: str = Depends(check_token_in_cookie)):
    return {"message": "Another access granted", "token": token}