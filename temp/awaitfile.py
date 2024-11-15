from fastapi import FastAPI, Request, Header, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import time

app = FastAPI()

# 가상의 유저 정보 조회 (refresh-token 검증)
@app.get("/sso/user-info")
async def get_user_info(authorization: Optional[str] = Header(None)):
    # 토큰이 있는지 확인
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token is required")

    # 여기서는 예제이므로 간단히 유저 정보를 반환
    # 실제로는 SSO 서버와 통신하여 유저 정보를 가져오는 로직을 구현해야 함
    token = authorization.split(" ")[1]
    if token == "valid-refresh-token":
        return {"name": "John Doe"}
    else:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

# 클라이언트에서 전송된 Header와 Body 데이터를 처리하는 엔드포인트
@app.post("/your-api-endpoint")
async def handle_custom_request(request: Request, header_key: Optional[str] = Header(None)):
    body = await request.json()
    # 전송된 데이터 출력 (실제로는 데이터 검증이나 처리 로직이 필요할 수 있음)
    return {
        "received_header_key": header_key,
        "received_body": body
    }

# 실시간 정보를 제공하는 엔드포인트
@app.get("/call/info")
async def get_info_data():
    # 갱신될 정보를 반환 (예: 현재 시간)
    return {"data": {"current_time": time.strftime('%Y-%m-%d %H:%M:%S')}}
    
    
    
    
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Info Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        #user-info {
            position: absolute;
            top: 10px;
            right: 10px;
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
        }
        #header-body-form {
            position: absolute;
            top: 10px;
            left: 10px;
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
        }
        #info-component {
            margin-top: 100px;
            width: 80%;
            padding: 20px;
            background-color: #e8f4fa;
            border-radius: 5px;
            white-space: pre-wrap;
            overflow-wrap: break-word;
        }
    </style>
    <script>
        // SSO 토큰을 사용해 유저 정보를 가져오는 함수
        async function fetchUserInfo() {
            try {
                const response = await fetch("/sso/user-info", {
                    headers: { "Authorization": "Bearer " + localStorage.getItem("refresh-token") }
                });
                if (response.ok) {
                    const userInfo = await response.json();
                    document.getElementById("user-info").innerText = `User: ${userInfo.name}`;
                } else {
                    document.getElementById("user-info").innerText = "Failed to fetch user info";
                }
            } catch (error) {
                console.error("Error fetching user info:", error);
                document.getElementById("user-info").innerText = "Error fetching user info";
            }
        }

        // Header와 Body 데이터를 서버로 전송하는 함수
        async function sendRequest() {
            const headerKey = document.getElementById("header-key").value;
            const headerValue = document.getElementById("header-value").value;
            const bodyKey = document.getElementById("body-key").value;
            const bodyValue = document.getElementById("body-value").value;

            try {
                const response = await fetch("/your-api-endpoint", {
                    method: "POST",
                    headers: {
                        [headerKey]: headerValue,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ [bodyKey]: bodyValue })
                });
                const result = await response.json();
                alert("Request sent. Server response: " + JSON.stringify(result));
            } catch (error) {
                console.error("Error sending request:", error);
                alert("Error sending request.");
            }
        }

        // /call/info 엔드포인트에서 실시간 정보를 가져오는 함수
        async function fetchInfo() {
            try {
                const response = await fetch("/call/info");
                if (response.ok) {
                    const result = await response.json();
                    document.getElementById("info-component").innerText = JSON.stringify(result.data, null, 2);
                } else {
                    document.getElementById("info-component").innerText = "Failed to fetch info";
                }
            } catch (error) {
                console.error("Error fetching info:", error);
                document.getElementById("info-component").innerText = "Error fetching info";
            }
        }

        // 주기적으로 /call/info 호출
        setInterval(fetchInfo, 5000); // 5초마다 정보 갱신
        window.onload = fetchUserInfo; // 페이지 로드 시 유저 정보 가져오기
    </script>
</head>
<body>
    <div id="user-info">Loading user info...</div>

    <div id="header-body-form">
        <h3>Custom Request</h3>
        <label for="header-key">Header Key:</label>
        <input type="text" id="header-key" placeholder="Header Key">
        <br>
        <label for="header-value">Header Value:</label>
        <input type="text" id="header-value" placeholder="Header Value">
        <br><br>
        <label for="body-key">Body Key:</label>
        <input type="text" id="body-key" placeholder="Body Key">
        <br>
        <label for="body-value">Body Value:</label>
        <input type="text" id="body-value" placeholder="Body Value">
        <br><br>
        <button onclick="sendRequest()">Send Request</button>
    </div>

    <div id="info-component">Loading info...</div>
</body>
</html>
    
    
    