from fastapi import FastAPI
import uvicorn
import sys
import os
import h5py
import torch
import torch.nn as nn

app = FastAPI()

# 모델 아키텍처 정의 (원본 모델과 동일해야 합니다)
class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.fc = nn.Linear(3, 1)  # 입력 차원 3, 출력 차원 1

    def forward(self, x):
        return self.fc(x)

# 모델 로드
def load_model():
    # 새로운 모델 인스턴스 생성
    model = SimpleModel()

    # 'model.h5' 파일로부터 가중치 로드
    with h5py.File('model.h5', 'r') as h5f:
        loaded_weights = {}
        for key in h5f.keys():
            weight = h5f[key][()]
            loaded_weights[key] = torch.from_numpy(weight)

    # 모델에 가중치 로드
    model.load_state_dict(loaded_weights)
    model.eval()  # 평가 모드로 전환

    return model

model = load_model()

@app.post("/predict")
async def predict(data: dict):
    input_data = data.get('input_data')
    if input_data is None:
        return {'error': 'input_data is required'}

    # 입력 데이터를 torch.Tensor로 변환
    input_tensor = torch.tensor(input_data, dtype=torch.float32)
    # 필요한 경우 배치 차원 추가
    if input_tensor.dim() == 1:
        input_tensor = input_tensor.unsqueeze(0)

    # 모델 예측 수행
    with torch.no_grad():
        prediction = model(input_tensor)

    # 예측 결과를 리스트로 변환
    prediction_list = prediction.numpy().tolist()
    return {'prediction': prediction_list}

if __name__ == "__main__":
    # 포트 번호를 모델별로 다르게 설정해야 함
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    uvicorn.run("main:app", host="0.0.0.0", port=port)