import requests

url = 'http://localhost:8000/predict'
data = {
    'input_data': [0.1, 0.2, 0.3]  # 모델이 기대하는 입력 형식에 맞게 수정하세요
}

response = requests.post(url, json=data)
print(response.json())