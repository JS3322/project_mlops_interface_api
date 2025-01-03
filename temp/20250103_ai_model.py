import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

import os
import warnings
warnings.filterwarnings('ignore')

###############################################################################
# 1. 데이터 불러오기 및 전처리
###############################################################################
def load_data(train_path='train.csv', test_path='test.csv', target_col='target'):
    """
    - CSV 파일을 읽어 (X, y) 형태로 반환 (회귀문제)
    - 결측치 처리(단순 평균) 및 NumPy 변환까지 수행
    """
    if not os.path.exists(train_path) or not os.path.exists(test_path):
        raise FileNotFoundError("train.csv 혹은 test.csv 파일이 존재하지 않습니다.")
    
    # 1) CSV 불러오기
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    # 2) 결측치 처리 (간단히 평균으로 대체)
    train_df = train_df.fillna(train_df.mean())
    test_df = test_df.fillna(test_df.mean())
    
    # 3) 타깃 분리
    y_train = train_df[target_col].values
    y_test = test_df[target_col].values
    
    X_train = train_df.drop(columns=[target_col])
    X_test = test_df.drop(columns=[target_col])
    
    # 4) NumPy로 변환
    X_train = X_train.values.astype(np.float32)
    y_train = y_train.astype(np.float32)
    X_test = X_test.astype(np.float32)
    y_test = y_test.astype(np.float32)
    
    return X_train, y_train, X_test, y_test, train_df.columns.drop(target_col).tolist()


def scale_data(X_train, X_test):
    """
    - 간단한 표준화(평균 0, 표준편차 1)를 직접 구현
    - 직접 구현하였지만, 필요하다면 sklearn의 StandardScaler 등 사용 가능
    """
    mean = X_train.mean(axis=0)
    std = X_train.std(axis=0) + 1e-8  # 분산이 0이 되는 경우 방지용
    
    X_train_scaled = (X_train - mean) / std
    X_test_scaled = (X_test - mean) / std
    
    return X_train_scaled, X_test_scaled, mean, std


###############################################################################
# 2. Dataset, DataLoader 정의
###############################################################################
class RegressionDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y
        
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        x = self.X[idx]
        y = self.y[idx]
        return x, y


def create_dataloaders(X_train, y_train, X_test, y_test, batch_size=32):
    """
    회귀 문제용 DataLoader 생성
    """
    train_dataset = RegressionDataset(X_train, y_train)
    test_dataset = RegressionDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    return train_loader, test_loader


###############################################################################
# 3. 모델(MLP) 정의
###############################################################################
class MLP(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, output_dim=1):
        """
        회귀 문제이므로 출력 차원을 1로 설정
        """
        super(MLP, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
        
    def forward(self, x):
        return self.net(x)


###############################################################################
# 4. 학습 함수 (train_step, evaluate, train_loop)
###############################################################################
def train_step(model, optimizer, criterion, X_batch, y_batch):
    optimizer.zero_grad()
    preds = model(X_batch)
    loss = criterion(preds.squeeze(), y_batch)  # preds: (batch,1), y_batch: (batch,)
    loss.backward()
    optimizer.step()
    return loss.item()

def evaluate(model, criterion, data_loader, device='cpu'):
    model.eval()
    total_loss = 0.0
    total_samples = 0
    
    all_preds = []
    all_targets = []
    
    with torch.no_grad():
        for X_batch, y_batch in data_loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)
            
            preds = model(X_batch)
            loss = criterion(preds.squeeze(), y_batch)
            batch_size = y_batch.size(0)
            
            total_loss += loss.item() * batch_size
            total_samples += batch_size
            
            all_preds.append(preds.squeeze().cpu().numpy())
            all_targets.append(y_batch.cpu().numpy())
    
    avg_loss = total_loss / total_samples
    
    # 추가 지표 (MAE, R2 등 계산)
    all_preds = np.concatenate(all_preds, axis=0)
    all_targets = np.concatenate(all_targets, axis=0)
    
    mae = np.mean(np.abs(all_preds - all_targets))
    # 간단한 R2 score 계산
    ss_res = np.sum((all_targets - all_preds)**2)
    ss_tot = np.sum((all_targets - np.mean(all_targets))**2)
    r2 = 1 - ss_res / (ss_tot + 1e-8)
    
    model.train()  # 평가 끝나면 train 모드로 복귀
    return avg_loss, mae, r2

def train_loop(model, train_loader, test_loader, 
               epochs=50, lr=1e-3, device='cpu'):
    """
    기본 학습 루프
    """
    model.to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    for epoch in range(1, epochs+1):
        # train step
        model.train()
        running_loss = 0.0
        for X_batch, y_batch in train_loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)
            loss_val = train_step(model, optimizer, criterion, X_batch, y_batch)
            running_loss += loss_val
        
        # evaluation
        val_loss, val_mae, val_r2 = evaluate(model, criterion, test_loader, device)
        
        if epoch % 10 == 0 or epoch == epochs:
            print(f"[Epoch {epoch:3d}/{epochs}] "
                  f"Train Loss: {running_loss/len(train_loader):.4f} | "
                  f"Val MSE: {val_loss:.4f}, MAE: {val_mae:.4f}, R2: {val_r2:.4f}")
    
    return model


###############################################################################
# 5. 하이퍼파라미터 최적화(간단한 탐색 예시)
###############################################################################
def hyperparam_search(X_train, y_train, X_test, y_test, 
                      hidden_dims=[32, 64], lrs=[1e-3, 1e-4], 
                      batch_sizes=[32, 64], epochs=30, device='cpu'):
    """
    - 아주 간단한 하이퍼파라미터 탐색 (Grid Search)
    - 실제로는 Optuna, Ray Tune, Hyperopt 등 라이브러리를 쓰면 훨씬 편리
    """
    best_config = None
    best_score = float('inf')  # 여기서는 MSE 기준으로 최소값 찾기
    
    # 순차적으로 탐색
    for hd in hidden_dims:
        for lr in lrs:
            for bs in batch_sizes:
                train_loader, test_loader = create_dataloaders(X_train, y_train, X_test, y_test, batch_size=bs)
                
                model = MLP(input_dim=X_train.shape[1], hidden_dim=hd, output_dim=1)
                model = train_loop(model, train_loader, test_loader, epochs=epochs, lr=lr, device=device)
                
                # 최종 MSE를 평가
                criterion = nn.MSELoss()
                final_mse, _, _ = evaluate(model, criterion, test_loader, device)
                
                print(f"Config=[hd:{hd}, lr:{lr}, bs:{bs}] => Final MSE: {final_mse:.4f}")
                
                if final_mse < best_score:
                    best_score = final_mse
                    best_config = (hd, lr, bs)
    
    print("\n=== Best Config ===")
    print(f"HiddenDim={best_config[0]}, LR={best_config[1]}, BatchSize={best_config[2]}, MSE={best_score:.4f}")
    
    # 최적 파라미터로 모델 재학습 후 반환
    hd, lr, bs = best_config
    train_loader, test_loader = create_dataloaders(X_train, y_train, X_test, y_test, batch_size=bs)
    
    best_model = MLP(input_dim=X_train.shape[1], hidden_dim=hd, output_dim=1)
    best_model = train_loop(best_model, train_loader, test_loader, epochs=epochs, lr=lr, device=device)
    
    return best_model, best_config


###############################################################################
# 6. 피처 중요도 (Permutation Feature Importance) - 회귀
###############################################################################
def permutation_feature_importance(model, X_val, y_val, device='cpu', n_repeats=5):
    """
    - MLP에는 feature_importances_가 없으므로,
      Permutation Importance 방식을 예시로 구현
    - (1) 전체 성능 측정
    - (2) 각 피처 별로 값을 무작위로 섞고, 성능 변화 측정
    - (3) 성능이 많이 나빠질수록 해당 피처가 중요하다고 판단
    """
    model.eval()
    X_val_t = torch.tensor(X_val, dtype=torch.float32).to(device)
    y_val_t = torch.tensor(y_val, dtype=torch.float32).to(device)
    
    criterion = nn.MSELoss()
    
    # 전체 baseline 성능
    with torch.no_grad():
        baseline_preds = model(X_val_t).squeeze()
        baseline_loss = criterion(baseline_preds, y_val_t).item()
    
    importances = np.zeros(X_val.shape[1], dtype=np.float32)
    
    for col in range(X_val.shape[1]):
        losses = []
        for _ in range(n_repeats):
            # X_val 복사본 생성
            X_val_copy = X_val.copy()
            # 해당 컬럼만 랜덤 셔플
            np.random.shuffle(X_val_copy[:, col])
            
            X_val_copy_t = torch.tensor(X_val_copy, dtype=torch.float32).to(device)
            
            with torch.no_grad():
                preds = model(X_val_copy_t).squeeze()
                loss = criterion(preds, y_val_t).item()
            losses.append(loss)
        
        mean_loss = np.mean(losses)
        # 중요도 = (오염 후 손실 - baseline 손실)
        importances[col] = mean_loss - baseline_loss
        
    return importances


###############################################################################
# 7. 특정 피처 제거 후 모델 재학습
###############################################################################
def remove_features_and_retrain(model, X_train, y_train, X_test, y_test, 
                                feature_names, importances, threshold=0.0, device='cpu'):
    """
    - permutation importance가 threshold 이하인 피처를 제거
    - 제거 후 모델 재학습
    """
    # 중요도가 낮으면 => 음수이거나 threshold 이하 => 제거
    # (Permutation Importance에서 '높을수록' 중요한 피처)
    # importances가 작거나 음수면 별로 영향 없다 가정
    to_remove = [f for f, imp in zip(feature_names, importances) if imp <= threshold]
    print("제거할 피처:", to_remove)
    
    # 실제 index로도 매핑
    remove_idx = [i for i, imp in enumerate(importances) if imp <= threshold]
    
    # 재구성
    keep_idx = [i for i in range(len(feature_names)) if i not in remove_idx]
    
    X_train_new = X_train[:, keep_idx]
    X_test_new = X_test[:, keep_idx]
    new_feature_names = [feature_names[i] for i in keep_idx]
    
    # 새 모델 학습
    train_loader, test_loader = create_dataloaders(X_train_new, y_train, X_test_new, y_test, batch_size=32)
    
    # 기존 모델의 hidden_dim, lr 등을 알 수 없으므로 임의로 다시 설정(혹은 hyperparam_search 사용)
    new_model = MLP(input_dim=X_train_new.shape[1], hidden_dim=64, output_dim=1)
    new_model = train_loop(new_model, train_loader, test_loader, epochs=30, lr=1e-3, device=device)
    
    return new_model, X_train_new, X_test_new, new_feature_names


###############################################################################
# 8. 파인튜닝 (예시: 기존 모델 파라미터 일부 고정 후 미세 조정)
###############################################################################
def fine_tune_model(model, X_train, y_train, X_test, y_test, 
                    epochs=20, lr=1e-4, device='cpu'):
    """
    - 파라미터 일부만 학습시키거나, 전체를 다시 학습시키는 등 다양한 방법이 가능
    - 여기서는 간단히 '전체 파라미터'에 대해 더 적은 lr로 추가 학습
    """
    train_loader, test_loader = create_dataloaders(X_train, y_train, X_test, y_test, batch_size=32)
    
    model.to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    for epoch in range(1, epochs+1):
        model.train()
        running_loss = 0.0
        for X_batch, y_batch in train_loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)
            
            loss_val = train_step(model, optimizer, criterion, X_batch, y_batch)
            running_loss += loss_val
        
        val_mse, val_mae, val_r2 = evaluate(model, criterion, test_loader, device)
        
        if epoch % 5 == 0 or epoch == epochs:
            print(f"[Fine-tune Epoch {epoch:2d}/{epochs}] "
                  f"Train Loss: {running_loss/len(train_loader):.4f} | "
                  f"Val MSE: {val_mse:.4f}, MAE: {val_mae:.4f}, R2: {val_r2:.4f}")
    
    return model


###############################################################################
# 9. 앙상블(단순 평균)
###############################################################################
def ensemble_models(models, X_data, device='cpu'):
    """
    - models: list of trained PyTorch models
    - X_data: numpy array of shape (n_samples, n_features)
    - 단순히 예측값을 평균 내는 방식
    """
    X_t = torch.tensor(X_data, dtype=torch.float32).to(device)
    preds_list = []
    
    with torch.no_grad():
        for m in models:
            m.eval()
            pred = m(X_t).squeeze().cpu().numpy()
            preds_list.append(pred)
    
    # axis=0 기준으로 평균
    final_preds = np.mean(preds_list, axis=0)
    return final_preds


###############################################################################
# 메인 실행 예시
###############################################################################
def main():
    # CPU / GPU 선택
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print("Using device:", device)
    
    # -----------------------------
    # 1) 데이터 로드 & 전처리
    # -----------------------------
    X_train, y_train, X_test, y_test, feature_names = load_data(
        train_path='train.csv',
        test_path='test.csv',
        target_col='target'  # 예: 회귀 타깃 컬럼명
    )
    
    # 스케일링
    X_train_scaled, X_test_scaled, mean, std = scale_data(X_train, X_test)
    
    # -----------------------------
    # 2) 베이스라인 모델 학습
    # -----------------------------
    train_loader, test_loader = create_dataloaders(X_train_scaled, y_train, X_test_scaled, y_test, batch_size=32)
    base_model = MLP(input_dim=X_train_scaled.shape[1], hidden_dim=64, output_dim=1)
    print("\n=== [베이스라인 모델 학습] ===")
    base_model = train_loop(base_model, train_loader, test_loader, epochs=50, lr=1e-3, device=device)
    
    # -----------------------------
    # 3) 하이퍼파라미터 탐색
    # -----------------------------
    print("\n=== [하이퍼파라미터 탐색] ===")
    best_model, best_config = hyperparam_search(X_train_scaled, y_train, 
                                                X_test_scaled, y_test, 
                                                hidden_dims=[32, 64], 
                                                lrs=[1e-3, 5e-4], 
                                                batch_sizes=[32, 64], 
                                                epochs=30, 
                                                device=device)
    
    # -----------------------------
    # 4) 피처 중요도 분석 (Permutation)
    # -----------------------------
    print("\n=== [피처 중요도 분석] ===")
    importances = permutation_feature_importance(best_model, X_test_scaled, y_test, device=device, n_repeats=3)
    
    # 중요도 출력
    for fname, imp in sorted(zip(feature_names, importances), key=lambda x:x[1], reverse=True):
        print(f"{fname}: {imp:.4f}")
    
    # -----------------------------
    # 5) 특정 피처 제거 후 재학습
    #    (Permutation Importance가 0 이하인 피처 제거 예시)
    # -----------------------------
    print("\n=== [피처 제거 후 재학습] ===")
    new_model, X_train_reduced, X_test_reduced, new_feature_names = remove_features_and_retrain(
        best_model, 
        X_train_scaled, y_train, 
        X_test_scaled, y_test, 
        feature_names, importances, 
        threshold=0.0, 
        device=device
    )
    
    # -----------------------------
    # 6) 파인튜닝 (Fine-tune)
    # -----------------------------
    print("\n=== [파인튜닝] ===")
    tuned_model = fine_tune_model(new_model, 
                                  X_train_reduced, y_train, 
                                  X_test_reduced, y_test, 
                                  epochs=20, lr=1e-4, device=device)
    
    # -----------------------------
    # 7) 앙상블 예시 (base_model, best_model, tuned_model) 단순 평균
    # -----------------------------
    print("\n=== [앙상블] ===")
    ensemble_preds = ensemble_models([base_model, best_model, tuned_model], 
                                     X_test_reduced, device=device)
    
    # 앙상블 성능 확인
    # MSE, MAE, R2 계산
    mse = np.mean((ensemble_preds - y_test)**2)
    mae = np.mean(np.abs(ensemble_preds - y_test))
    ss_res = np.sum((y_test - ensemble_preds)**2)
    ss_tot = np.sum((y_test - np.mean(y_test))**2)
    r2 = 1 - ss_res/(ss_tot+1e-8)
    
    print(f"[Ensemble] MSE={mse:.4f}, MAE={mae:.4f}, R2={r2:.4f}")


if __name__ == "__main__":
    main()