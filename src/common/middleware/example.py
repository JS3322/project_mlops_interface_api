from fastapi import Request
import time

# from starlette.responses import JSONResponse

blocked_ips = ["192.168.1.1", "10.0.0.1"]

# 미들웨어 정의
async def add_process_time_header(request: Request, call_next):

    # 요청이 들어온 시간 기록
    start_time = time.time()

    ### blocking example
    # 요청을 보낸 클라이언트의 IP 주소
    client_ip = request.client.host
    # if client_ip in blocked_ips:
    #     return JSONResponse(status_code=403, content={"detail": "Forbidden"})
    print(f"Request: {request.method} {request.url} {client_ip}")

    response = await call_next(request)

    # 응답 상태 코드 로깅
    print(f"Response Status: {response.status_code}")



    # 요청을 처리하는 핸들러로 전달
    # response = await call_next(request)

    # 요청 처리 후 종료 시간 기록
    process_time = time.time() - start_time

    # 응답 헤더에 처리 시간 추가
    response.headers["X-Process-Time"] = str(process_time)

    return response