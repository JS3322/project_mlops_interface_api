import os
import time
import threading
import importlib.util
from typing import Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ray
from ray import serve

###################################
# 설정
MODEL_BASE_DIR = "/user/aaa/bbb"
MODEL_TTL = 3600        # 1시간(초)
CLEANUP_INTERVAL = 300  # 5분마다 정리

###################################
# 모델 관리 로직
model_cache: Dict[str, Dict] = {}
cache_lock = threading.Lock()

def load_model(model_name: str):
    model_dir = os.path.join(MODEL_BASE_DIR, model_name)
    main_path = os.path.join(model_dir, "main.py")
    if not os.path.exists(main_path):
        raise FileNotFoundError(f"Model {model_name} not found at {main_path}")

    spec = importlib.util.spec_from_file_location("model_module", main_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def get_model(model_name: str):
    with cache_lock:
        if model_name in model_cache:
            # 접근 시간 갱신
            model_cache[model_name]["last_access"] = time.time()
            return model_cache[model_name]["module"]
        # 모델 없는 경우 로딩
        module = load_model(model_name)
        model_cache[model_name] = {"module": module, "last_access": time.time()}
        return module

def cleanup_models():
    while True:
        time.sleep(CLEANUP_INTERVAL)
        now = time.time()
        with cache_lock:
            to_remove = [m for m, info in model_cache.items() if now - info["last_access"] > MODEL_TTL]
            for m in to_remove:
                del model_cache[m]

# 모델 정리 스레드 백그라운드 실행
cleanup_thread = threading.Thread(target=cleanup_models, daemon=True)
cleanup_thread.start()

###################################
# FastAPI 정의
app = FastAPI()

class PredictRequest(BaseModel):
    model_name: str
    pred_type: str
    args: dict

@app.post("/predict")
def predict(req: PredictRequest):
    try:
        model_module = get_model(req.model_name)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # 장기 실행 가능
    result = model_module.run_prediction(req.pred_type, **req.args)
    return {"status": "done", "result": result}

###################################
# Ray Serve 설정
if __name__ == "__main__":
    # 로컬에서 Ray 초기화 (클러스터 사용 시 address="auto" 가능)
    ray.init()
    serve.start(http_options={"host": "0.0.0.0", "port": 8000})

    @serve.deployment(name="model_service", route_prefix="/", num_replicas=2)
    @serve.ingress(app)
    class ModelService:
        pass

    ModelService.deploy()