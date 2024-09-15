from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    response.headers['X-Process-Time'] = "time calculation here"
    return response