/user/viststorage/mlops/supervisor_env/bin/supervisorctl -c /user/viststorage/mlops/supervisor_conf/supervisord.conf start app1

/user/viststorage/mlops/supervisor_env/bin/supervisorctl -c /user/viststorage/mlops/supervisor_conf/supervisord.conf stop app1

import os
import time
from datetime import datetime, timedelta

# 애플리케이션 상태 관리
app_status = {
    "app1": {"last_called": None},
    "app2": {"last_called": None},
    "app3": {"last_called": None},
}

# Supervisor 명령 실행 함수
def supervisor_command(command, app_name):
    os.system(f"/user/viststorage/mlops/supervisor_env/bin/supervisorctl -c /user/viststorage/mlops/supervisor_conf/supervisord.conf {command} {app_name}")

# 애플리케이션 실행 함수
def start_app(app_name):
    supervisor_command("start", app_name)
    app_status[app_name]["last_called"] = datetime.now()
    print(f"{app_name} started at {app_status[app_name]['last_called']}")

# 애플리케이션 중지 함수
def stop_app(app_name):
    supervisor_command("stop", app_name)
    app_status[app_name]["last_called"] = None
    print(f"{app_name} stopped")

# 호출 처리 함수
def handle_request(app_name):
    if app_status[app_name]["last_called"] is None:
        start_app(app_name)
    else:
        app_status[app_name]["last_called"] = datetime.now()
        print(f"{app_name} called at {app_status[app_name]['last_called']}")

# 애플리케이션 상태 모니터링 함수
def monitor_apps():
    while True:
        for app_name, status in app_status.items():
            if status["last_called"]:
                elapsed = datetime.now() - status["last_called"]
                if elapsed > timedelta(hours=1):
                    stop_app(app_name)
        time.sleep(60)  # 1분 간격으로 상태 확인

if __name__ == "__main__":
    # 테스트 요청
    handle_request("app1")  # app1 호출
    time.sleep(5)           # 5초 후 app2 호출
    handle_request("app2")

    # 상태 모니터링 시작
    monitor_apps()