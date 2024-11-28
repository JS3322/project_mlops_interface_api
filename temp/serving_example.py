# 필요한 라이브러리 임포트
import os
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import runpy

# 모델 상태를 저장할 딕셔너리와 락 생성
model_states = {}
model_lock = threading.Lock()

# 모델 디렉토리 경로
model_dir = '/user/viststorage2/mlops/model_list/'

# 모델 로드 함수
def load_models():
    with model_lock:
        for model_name in os.listdir(model_dir):
            model_path = os.path.join(model_dir, model_name)
            if os.path.isdir(model_path):
                load_model(model_name)

def load_model(model_name):
    model_path = os.path.join(model_dir, model_name)
    main_py = os.path.join(model_path, 'main.py')
    if os.path.exists(main_py):
        # runpy를 사용하여 __main__ 실행
        globals_dict = {}
        runpy.run_path(main_py, init_globals=globals_dict)
        # 모델 상태 저장 (필요한 경우)
        with model_lock:
            model_states[model_name] = globals_dict.get('model_state', {})
        print(f"Model '{model_name}' loaded via __main__.")

def reload_model(model_name):
    with model_lock:
        if model_name in model_states:
            del model_states[model_name]
        load_model(model_name)
        print(f"Model '{model_name}' reloaded via __main__.")

# 파일 시스템 감시 핸들러 클래스
class ModelDirectoryHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            model_name = os.path.basename(event.src_path)
            load_model(model_name)
    def on_modified(self, event):
        if event.is_directory:
            model_name = os.path.basename(event.src_path)
            reload_model(model_name)

# 파일 시스템 감시 시작 함수
def start_watcher():
    event_handler = ModelDirectoryHandler()
    observer = Observer()
    observer.schedule(event_handler, path=model_dir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

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
        if model_name not in model_states:
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found.")
        globals_dict = model_states[model_name]

    # '__main__'으로 실행된 코드에서 필요한 함수 호출
    if 'run' in globals_dict:
        try:
            result = globals_dict['run'](**arguments)
            return {"result": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail=f"Model '{model_name}' does not have a 'run' function in __main__.")

# 서버 실행
if __name__ == "__main__":
    # 모델 로드
    load_models()
    # 파일 시스템 감시 시작
    watcher_thread = threading.Thread(target=start_watcher)
    watcher_thread.daemon = True
    watcher_thread.start()
    # FastAPI 앱 실행
    uvicorn.run("your_script_name:app", host="0.0.0.0", port=8000)