from fastapi import HTTPException, status, APIRouter, Depends

from src.ml.domain.service.execute_request_info_db import insert_request_info, read_request_info
from src.ml.domain.vo.request_info_vo import RequestInfoVO
from fastapi.security import OAuth2PasswordBearer
from fastapi import BackgroundTasks
import logging
from src.common.di.example import get_db
import multiprocessing
import subprocess
import time
import threading
import psutil

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def write_log(message: str):
    with open("log.txt", mode="a") as log:
        log.write(message)

route = APIRouter()
logger = logging.getLogger("default")
# db=Depends(get_db)
# , token: str = Depends(oauth2_scheme)

running_processes = []
process_lock = threading.Lock()
MAX_PROCESSES = 3  # 최대 프로세스 수 제한

def create_virtual_env():
    print("함수 origin 실행 시작")
    time.sleep(10)  # 실제 작업을 시뮬레이션하기 위한 지연
    print("함수 origin 실행 완료")

def long_computation_function1():
    print("함수 1 실행 시작")
    time.sleep(5)  # 실제 작업을 시뮬레이션하기 위한 지연
    print("함수 1 실행 완료")

def long_computation_function2():
    print("함수 2 실행 시작")
    time.sleep(5)  # 실제 작업을 시뮬레이션하기 위한 지연
    print("함수 2 실행 완료")

def run_tasks_sequentially():
    create_virtual_env()
    long_computation_function1()
    long_computation_function2()
    print("모든 작업 완료")

def process_finished_callback(process):
    with process_lock:
        if process in running_processes:
            running_processes.remove(process)
            print(f"프로세스 {process.pid} 종료 및 리스트에서 제거")

def wait_for_process(process):
    process.join()
    process_finished_callback(process)

def run_in_process():
    p = multiprocessing.Process(target=run_tasks_sequentially)
    p.start()
    print(f"프로세스 {p.pid} 시작")
    threading.Thread(target=wait_for_process, args=(p,)).start()
    return p

@route.post("/async")
async def execute_sample(background_tasks: BackgroundTasks, request_info: RequestInfoVO):
    try:
        # 로그에 요청 정보 기록
        logger.info(f"Received request: {request_info}")

        # 요청 정보를 JSON 형식으로 변환
        request_data = request_info.dict()

        background_tasks.add_task(write_log, f"Notification sent to {request_data}")

        with process_lock:
            # 실행 중인 프로세스 리스트를 정리하여 종료된 프로세스 제거
            running_processes[:] = [p for p in running_processes if p.is_alive()]
            if len(running_processes) >= MAX_PROCESSES:
                raise HTTPException(status_code=429, detail="최대 프로세스 수에 도달했습니다. 잠시 후 다시 시도해주세요.")
            else:
                # 새로운 프로세스를 시작하고 리스트에 추가
                p = run_in_process()
                running_processes.append(p)

        return {
            "result": "success",
            "data": request_data
        }
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@route.get("/status")
async def get_status():
    with process_lock:
        # 실행 중인 프로세스 수 계산
        current_processes = len(running_processes)

    # 전체 메모리 정보 가져오기
    try:
        memory_info = psutil.virtual_memory()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메모리 정보를 가져오는 중 오류 발생: {e}")

    # 필요한 정보 선택
    total_memory = memory_info.total  # 총 메모리 (바이트 단위)
    used_memory = memory_info.used    # 사용 중인 메모리 (바이트 단위)
    available_memory = memory_info.available  # 사용 가능한 메모리 (바이트 단위)
    memory_usage_percent = memory_info.percent  # 메모리 사용률 (%)
    cpu_usage_percent = psutil.cpu_percent(interval=1)

    return {
        "current_processes": current_processes,
        "max_processes": MAX_PROCESSES,
        "memory": {
            "total_memory": total_memory,
            "used_memory": used_memory,
            "available_memory": available_memory,
            "memory_usage_percent": memory_usage_percent
        },
        "cpu": {
            "cpu_usage_percent": cpu_usage_percent
        }
    }

@route.post("/example")
async def execute_sample(background_tasks: BackgroundTasks, request_info: RequestInfoVO):
    try:
        # 로그에 요청 정보 기록
        logger.info(f"Received request: {request_info}")

        # 요청 정보를 JSON 형식으로 변환
        request_data = request_info.dict()

        background_tasks.add_task(write_log, f"Notification sent to {request_data}")

        return {
            "result": "success",
            "data": request_data
        }
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@route.post("/example/db")
async def execute_sample_db(background_tasks: BackgroundTasks, request_info: RequestInfoVO):
    try:
        # 로그에 요청 정보 기록
        logger.info(f"Received request: {request_info}")

        # 요청 정보를 데이터베이스에 저장
        insert_request_info(request_info)

        return {
            "result": "success",
            "data": "test"
        }
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@route.get("/example/db/{item_id}")
async def read_example_db(item_id: int):
    try:
        # 로그에 요청 정보 기록
        logger.info(f"Received request to read item with ID: {item_id}")

        # 데이터베이스에서 요청 정보 읽기
        request_info = read_request_info(item_id)

        return {
            "result": "success",
            "data": request_info
        }
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )   