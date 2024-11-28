import importlib.util
import os

# 모델 모듈을 저장할 딕셔너리
model_modules = {}

# 모델 디렉토리 경로
model_dir = '/user/viststorage2/mlops/model_list/'

def load_models():
    for model_name in os.listdir(model_dir):
        model_path = os.path.join(model_dir, model_name)
        if os.path.isdir(model_path):
            main_py = os.path.join(model_path, 'main.py')
            if os.path.exists(main_py):
                # 모듈 임포트
                spec = importlib.util.spec_from_file_location(f"{model_name}_main", main_py)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # 딕셔너리에 저장
                model_modules[model_name] = module
                
                
                
                
                
                
                
                
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI()

class ModelRequest(BaseModel):
    model_name: str
    arguments: Dict[str, Any]

@app.post("/execute")
async def execute_model(request: ModelRequest):
    model_name = request.model_name
    arguments = request.arguments

    if model_name not in model_modules:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found.")

    model_module = model_modules[model_name]

    # 'run' 함수를 호출하여 모델 실행
    if hasattr(model_module, 'run'):
        try:
            result = model_module.run(**arguments)
            return {"result": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail=f"Model '{model_name}' does not have a 'run' function.")
        
        
        
        
        
        
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

class ModelDirectoryHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            model_name = os.path.basename(event.src_path)
            load_model(model_name)
    def on_modified(self, event):
        if event.is_directory:
            model_name = os.path.basename(event.src_path)
            reload_model(model_name)

def load_model(model_name):
    model_path = os.path.join(model_dir, model_name)
    main_py = os.path.join(model_path, 'main.py')
    if os.path.exists(main_py):
        spec = importlib.util.spec_from_file_location(f"{model_name}_main", main_py)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        model_modules[model_name] = module
        print(f"Model '{model_name}' loaded.")

def reload_model(model_name):
    # 기존 모듈 제거
    if model_name in model_modules:
        del model_modules[model_name]
    # 모델 다시 로드
    load_model(model_name)
    print(f"Model '{model_name}' reloaded.")

def start_watcher():
    event_handler = ModelDirectoryHandler()
    observer = Observer()
    observer.schedule(event_handler, path=model_dir, recursive=False)
    observer.start()
    
    
    
import uvicorn

if __name__ == "__main__":
    # 모델 로드
    load_models()
    # 파일 시스템 감시 시작
    watcher_thread = threading.Thread(target=start_watcher)
    watcher_thread.daemon = True
    watcher_thread.start()
    # FastAPI 앱 실행
    uvicorn.run("your_script_name:app", host="0.0.0.0", port=8000)