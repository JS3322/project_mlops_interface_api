import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import h5py

# 데이터 생성
np.random.seed(0)
x_data = np.random.rand(100, 3)  # 100개의 샘플, 3개의 특성(x, y, z)
y_data = np.sum(x_data, axis=1)  # 목표값: x, y, z의 합

# Tensor로 변환
x_tensor = torch.from_numpy(x_data).float()
y_tensor = torch.from_numpy(y_data).float().unsqueeze(1)

# 데이터로더 생성
dataset = torch.utils.data.TensorDataset(x_tensor, y_tensor)
dataloader = torch.utils.data.DataLoader(dataset, batch_size=16, shuffle=True)

# 모델 정의
class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.fc = nn.Linear(3, 1)

    def forward(self, x):
        return self.fc(x)

model = SimpleModel()

# 손실 함수 및 옵티마이저 정의
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# 모델 훈련
num_epochs = 100
for epoch in range(num_epochs):
    for inputs, targets in dataloader:
        outputs = model(inputs)
        loss = criterion(outputs, targets)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    if (epoch+1) % 20 == 0:
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

# 모델 가중치 저장
model_weights = model.state_dict()
weights_np = {key: model_weights[key].numpy() for key in model_weights}

with h5py.File('model.h5', 'w') as h5f:
    for key in weights_np:
        h5f.create_dataset(key, data=weights_np[key])

# 새로운 모델에 가중치 로드
loaded_model = SimpleModel()
with h5py.File('model.h5', 'r') as h5f:
    loaded_weights = {key: torch.from_numpy(h5f[key][()]) for key in h5f.keys()}

loaded_model.load_state_dict(loaded_weights)

# 예측 테스트
test_data = np.array([[0.1, 0.2, 0.3]])
test_tensor = torch.from_numpy(test_data).float()

model.eval()
loaded_model.eval()

with torch.no_grad():
    original_output = model(test_tensor)
    loaded_output = loaded_model(test_tensor)

print(f'Original Model Prediction: {original_output.item():.4f}')
print(f'Loaded Model Prediction: {loaded_output.item():.4f}')