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
MODEL_TTL = 3600        # 1시간 (초)
CLEANUP_INTERVAL = 300  # 5분마다 정리

###################################
# FastAPI 정의
app = FastAPI()

class PredictRequest(BaseModel):
    model_name: str
    pred_type: str
    args: dict

@app.post("/predict")
def predict(req: PredictRequest):
    # 이 엔드포인트 로직은 ModelService 클래스에서 처리하도록 할 것이므로,
    # 여기에서는 단순히 ModelService의 예측 메서드를 호출하도록 구성할 예정.
    # serve.ingress(app)로 app을 ModelService와 연결하면,
    # ModelService.__call__ 또는 ModelService 내부 메서드로 요청이 들어오지 않습니다.
    #
    # Ray Serve 2.x 이후로는 FastAPI 라우트를 ModelService 클래스 외부에서 정의하고,
    # @serve.ingress(app)을 통해 클래스에 바인딩하면,
    # 요청 처리를 위해 클래스 인스턴스 메서드에 접근하려면 Dependency Injection 또는
    # 클래스 속성 접근 방식을 사용해야 합니다.
    #
    # 여기서는 ModelService 인스턴스에 접근하기 위해 Ray Serve의 handle을 사용할 수 있지만,
    # 단순화를 위해 ModelService 클래스 내부에서 엔드포인트를 구현하겠습니다.
    #
    # 따라서 이 부분은 제거하거나, ModelService 클래스에서 처리하도록 수정하겠습니다.
    pass

###################################
# Ray Serve 설정
@serve.deployment(name="model_service", num_replicas=2)
@serve.ingress(app)
class ModelService:
    def __init__(self):
        # 전역 변수가 아닌, 클래스 내부에서 lock, cache 등을 초기화
        self.model_cache: Dict[str, Dict] = {}
        self.cache_lock = threading.Lock()
        
        # 백그라운드 모델 정리 쓰레드 시작
        self.cleanup_thread = threading.Thread(target=self.cleanup_models, daemon=True)
        self.cleanup_thread.start()

    def load_model(self, model_name: str):
        model_dir = os.path.join(MODEL_BASE_DIR, model_name)
        main_path = os.path.join(model_dir, "main.py")
        if not os.path.exists(main_path):
            raise FileNotFoundError(f"Model {model_name} not found at {main_path}")

        spec = importlib.util.spec_from_file_location("model_module", main_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def get_model(self, model_name: str):
        with self.cache_lock:
            if model_name in self.model_cache:
                self.model_cache[model_name]["last_access"] = time.time()
                return self.model_cache[model_name]["module"]
            module = self.load_model(model_name)
            self.model_cache[model_name] = {"module": module, "last_access": time.time()}
            return module

    def cleanup_models(self):
        while True:
            time.sleep(CLEANUP_INTERVAL)
            now = time.time()
            with self.cache_lock:
                to_remove = [m for m, info in self.model_cache.items() if now - info["last_access"] > MODEL_TTL]
                for m in to_remove:
                    del self.model_cache[m]

    @app.post("/predict")
    def handle_predict(self, req: PredictRequest):
        try:
            model_module = self.get_model(req.model_name)
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

        # 장기 실행 가능
        result = model_module.run_prediction(req.pred_type, **req.args)
        return {"status": "done", "result": result}


if __name__ == "__main__":
    # 로컬에서 Ray 초기화
    ray.init()
    # 모델 서비스를 라우트 프리픽스 "/"에 배포
    serve.run(ModelService.bind(), name="model_service", route_prefix="/")