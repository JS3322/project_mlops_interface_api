# main.py (각 모델의 디렉토리에 위치)

from fastapi import FastAPI
import uvicorn
import sys
import os

# 필요한 패키지 임포트 (가상환경 내에 설치되어 있어야 함)
import tensorflow as tf  # 또는 PyTorch 등

app = FastAPI()

# 모델 로드
def load_model():
    model = tf.keras.models.load_model('model.h5')
    return model

model = load_model()

@app.post("/predict")
async def predict(data: dict):
    input_data = data.get('input_data')
    # 모델 예측 수행
    prediction = model.predict(input_data)
    return {'prediction': prediction.tolist()}

if __name__ == "__main__":
    # 포트 번호를 모델별로 다르게 설정해야 함
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    uvicorn.run("main:app", host="0.0.0.0", port=port)