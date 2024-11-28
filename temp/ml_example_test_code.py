import torch
import torch.nn as nn
import numpy as np
import h5py

# 모델 정의 (원본 모델과 동일한 아키텍처)
class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.fc = nn.Linear(3, 1)  # 입력 3차원(x, y, z), 출력 1차원

    def forward(self, x):
        return self.fc(x)

def test_model():
    # 새로운 모델 인스턴스 생성
    model = SimpleModel()
    
    # 'model.h5' 파일로부터 가중치 로드
    with h5py.File('model.h5', 'r') as h5f:
        loaded_weights = {key: torch.from_numpy(h5f[key][()]) for key in h5f.keys()}
    
    model.load_state_dict(loaded_weights)
    model.eval()  # 평가 모드로 전환

    print("모델 가중치를 'model.h5' 파일로부터 성공적으로 로드하였습니다.")

    # 테스트 입력 데이터 생성
    # 입력 데이터와 예상 출력 값을 리스트로 저장
    test_inputs = [
        np.array([[0.1, 0.2, 0.3]]),
        np.array([[0.5, 0.5, 0.5]]),
        np.array([[1.0, 2.0, 3.0]]),
        np.array([[0.0, 0.0, 0.0]]),
    ]

    # 예상 결과 계산 (입력의 합)
    expected_outputs = [np.sum(inp) for inp in test_inputs]

    # 모델 예측 및 결과 비교
    with torch.no_grad():
        for i, test_input in enumerate(test_inputs):
            input_tensor = torch.from_numpy(test_input).float()
            prediction = model(input_tensor).item()
            expected = expected_outputs[i]
            print(f"입력: {test_input.flatten()}")
            print(f"모델 예측값: {prediction:.4f}, 예상값: {expected:.4f}")
            if np.isclose(prediction, expected, atol=0.01):
                print("→ 예측이 예상값과 일치합니다.\n")
            else:
                print("→ 예측이 예상값과 일치하지 않습니다.\n")