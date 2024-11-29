import os
import threading
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import requests

# 모델 상태를 저장할 딕셔너리와 락 생성
model_servers = {}  # 모델 이름과 해당 서버의 주소를 저장
model_lock = threading.Lock()

# 모델 디렉토리 경로
model_dir = '/user/viststorage2/mlops/model_list/'

# 모델 로드 함수
def load_models():
    with model_lock:
        for model_name in os.listdir(model_dir):
            model_path = os.path.join(model_dir, model_name)
            if os.path.isdir(model_path):
                start_model_server(model_name)

def start_model_server(model_name):
    model_path = os.path.join(model_dir, model_name)
    main_py = os.path.join(model_path, 'main.py')
    if os.path.exists(main_py):
        # 가상환경의 Python 인터프리터 경로
        venv_python = os.path.join(model_path, 'venv', 'bin', 'python')
        if not os.path.exists(venv_python):
            print(f"가상환경이 존재하지 않습니다: {venv_python}")
            return

        # 포트 번호를 모델마다 다르게 설정
        port = 8000 + len(model_servers) + 1  # 포트 번호 설정
        # 모델 서버 실행
        process = threading.Thread(target=run_model_server, args=(venv_python, main_py, port, model_name))
        process.daemon = True
        process.start()

        # 모델 서버 주소 저장
        with model_lock:
            model_servers[model_name] = f"http://localhost:{port}"
        print(f"Model '{model_name}' server started at port {port}.")

def run_model_server(python_executable, main_py, port, model_name):
    import subprocess
    subprocess.run([python_executable, main_py, str(port)], cwd=os.path.dirname(main_py))

# FastAPI 인스턴스 생성
app = FastAPI()

# 요청 모델 정의
class ModelRequest(BaseModel):
    model_name: str
    arguments: Dict[str, Any]

# 엔드포인트 정의
@app.post("/execute")
async def execute_model(request: ModelRequest):
    model_name = request.model_name
    arguments = request.arguments

    with model_lock:
        if model_name not in model_servers:
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found.")
        model_server_url = model_servers[model_name]

    # 모델 서버에 예측 요청 보내기
    try:
        response = requests.post(f"{model_server_url}/predict", json=arguments)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 서버 실행
if __name__ == "__main__":
    # 모델 로드
    load_models()
    # FastAPI 앱 실행
    import uvicorn
    uvicorn.run("your_script_name:app", host="0.0.0.0", port=8000)