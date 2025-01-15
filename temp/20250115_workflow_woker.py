import psycopg2
from psycopg2.extras import RealDictCursor
import time
from threading import Thread, Lock

# PostgreSQL 연결 설정
DB_CONFIG = {
    "dbname": "your_db",
    "user": "your_user",
    "password": "your_password",
    "host": "localhost",
    "port": 5432,
}

lock = Lock()  # 중복 실행 방지

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def execute_job(job):
    """
    실제 Job 실행 로직
    """
    job_id = job["id"]
    job_type = job["job_type"]
    parameters = job["parameters"]

    print(f"Executing Job {job_id} of type {job_type}...")

    # Job Type에 따른 처리
    if job_type == "doe":
        time.sleep(5)  # 예: DOE 작업 실행
        print(f"Job {job_id} completed: DOE with parameters {parameters}.")
    elif job_type == "preprocess":
        time.sleep(3)  # 예: Preprocess 작업 실행
        print(f"Job {job_id} completed: Preprocess with parameters {parameters}.")
    else:
        print(f"Unknown Job Type: {job_type}")

def worker():
    """
    Worker가 DB에서 Job을 가져와 실행
    """
    while True:
        with lock:  # 중복 실행 방지
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # 실행 대기 중인 Job 하나 가져오기
            cursor.execute("""
            SELECT * FROM job_queue
            WHERE id NOT IN (
                SELECT job_id FROM job_status_log WHERE status IN ('running', 'complete')
            )
            ORDER BY created_at ASC
            LIMIT 1;
            """)
            job = cursor.fetchone()

            if job:
                # Job 상태를 Running으로 삽입
                cursor.execute("""
                INSERT INTO job_status_log (job_id, status, updated_at)
                VALUES (%s, %s, NOW());
                """, (job["id"], "running"))
                conn.commit()

                cursor.close()
                conn.close()

                # Job 실행
                execute_job(job)

                # Job 상태를 Complete으로 삽입
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO job_status_log (job_id, status, updated_at)
                VALUES (%s, %s, NOW());
                """, (job["id"], "complete"))
                conn.commit()

                cursor.close()
                conn.close()
            else:
                cursor.close()
                conn.close()
                time.sleep(1)  # 대기 상태로 돌아감

# Worker 실행 (멀티스레드)
if __name__ == "__main__":
    num_workers = 3  # 병렬로 실행할 Worker 수
    threads = [Thread(target=worker) for _ in range(num_workers)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
        
        
        
        
        
        
        
        


import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
import requests
import time

# PostgreSQL 연결 설정
DB_CONFIG = {
    "dbname": "your_db",
    "user": "your_user",
    "password": "your_password",
    "host": "localhost",
    "port": 5432,
}

# API URL 설정
API_URL = "http://localhost:8000/execute-job"

def get_db_connection():
    """
    PostgreSQL DB 연결 생성
    """
    return psycopg2.connect(**DB_CONFIG)

def call_api(job_id, job_type, parameters):
    """
    Job API 호출
    """
    try:
        payload = {
            "job_id": job_id,
            "job_type": job_type,
            "parameters": parameters
        }
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()  # 요청 중 오류 발생 시 예외 발생
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API 호출 실패: {e}")
        return {"status": "error", "message": str(e)}

def worker():
    """
    Worker가 Job Queue에서 Job을 가져와 API를 호출
    """
    worker_id = str(uuid.uuid4())  # Worker 고유 ID 생성
    print(f"Worker {worker_id} 시작")

    while True:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # 실행 대기 중인 Job 하나 가져오기
            cursor.execute("""
            WITH cte AS (
                SELECT id, job_type, parameters
                FROM job_queue
                WHERE id NOT IN (
                    SELECT job_id FROM job_status_log WHERE status IN ('running', 'complete')
                )
                ORDER BY created_at ASC
                LIMIT 1
                FOR UPDATE SKIP LOCKED
            )
            UPDATE job_queue
            SET updated_at = NOW()
            WHERE id = (SELECT id FROM cte)
            RETURNING id, job_type, parameters;
            """)
            job = cursor.fetchone()

            if job:
                job_id, job_type, parameters = job["id"], job["job_type"], job["parameters"]

                # Job 상태를 Running으로 기록
                cursor.execute("""
                INSERT INTO job_status_log (job_id, status, updated_at)
                VALUES (%s, %s, NOW());
                """, (job_id, "running"))
                conn.commit()

                # API 호출
                print(f"Job {job_id} 실행 시작 (Type: {job_type})")
                response = call_api(job_id, job_type, parameters)
                print(f"Job {job_id} 실행 완료: {response}")

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Worker Error: {str(e)}")
        finally:
            time.sleep(1)  # 1초 대기 후 다시 실행

def main():
    """
    Main 함수 - Worker 실행
    """
    print("Worker를 시작합니다...")
    worker()

if __name__ == "__main__":
    main()
    
    
    
    
    
    
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
import requests
import time

# PostgreSQL 연결 설정
DB_CONFIG = {
    "dbname": "your_db",
    "user": "your_user",
    "password": "your_password",
    "host": "localhost",
    "port": 5432",
}

# Job API URL
API_URL = "http://localhost:8000/execute-job"

def get_db_connection():
    """
    PostgreSQL DB 연결 생성
    """
    return psycopg2.connect(**DB_CONFIG)

def call_api(kit_id, job_name, parameters):
    """
    Job API 호출
    """
    try:
        payload = {
            "kit_id": kit_id,
            "job_name": job_name,
            "parameters": parameters
        }
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()  # 요청 중 오류 발생 시 예외 발생
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API 호출 실패: {e}")
        return {"status": "error", "message": str(e)}

def worker():
    """
    Worker가 Job Queue에서 Job을 가져와 API를 호출
    """
    worker_id = str(uuid.uuid4())  # Worker 고유 ID 생성
    print(f"Worker {worker_id} 시작")

    while True:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # 실행 대기 중인 Job 하나 가져오기 및 Lock 설정
            cursor.execute("""
            WITH cte AS (
                SELECT kit_id, job_name, parameters
                FROM vista_test.vist_ml_management_job_queue
                WHERE (locked_by IS NULL OR lock_time < CURRENT_TIMESTAMP - INTERVAL '10 minutes')
                AND kit_id NOT IN (
                    SELECT kit_id FROM vistadb_test.vist_ml_management_job_log WHERE status IN ('running', 'complete')
                )
                ORDER BY crate_at ASC
                LIMIT 1
            )
            UPDATE vista_test.vist_ml_management_job_queue
            SET locked_by = %s, lock_time = CURRENT_TIMESTAMP
            WHERE kit_id = (SELECT kit_id FROM cte)
            RETURNING kit_id, job_name, parameters;
            """, (worker_id,))
            job = cursor.fetchone()

            if job:
                kit_id, job_name, parameters = job["kit_id"], job["job_name"], job["parameters"]

                # Job 상태를 Running으로 기록
                cursor.execute("""
                INSERT INTO vistadb_test.vist_ml_management_job_log (kit_id, status, crateed_at)
                VALUES (%s, %s, TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS'));
                """, (kit_id, "running"))
                conn.commit()

                # API 호출
                print(f"Job 실행 시작 (Kit ID: {kit_id}, Job Name: {job_name})")
                response = call_api(kit_id, job_name, parameters)
                print(f"Job 실행 완료: {response}")

                # Job 상태를 Complete으로 기록
                cursor.execute("""
                INSERT INTO vistadb_test.vist_ml_management_job_log (kit_id, status, crateed_at)
                VALUES (%s, %s, TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS'));
                """, (kit_id, "complete"))
                conn.commit()

                # Job Lock 해제 (optional: 상태가 Complete인 Job은 Lock 해제)
                cursor.execute("""
                UPDATE vista_test.vist_ml_management_job_queue
                SET locked_by = NULL, lock_time = NULL
                WHERE kit_id = %s;
                """, (kit_id,))
                conn.commit()

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Worker Error: {str(e)}")
        finally:
            time.sleep(1)  # 1초 대기 후 다시 실행

def main():
    """
    Main 함수 - Worker 실행
    """
    print("Worker를 시작합니다...")
    worker()

if __name__ == "__main__":
    main()
    
    
    
    
WITH cte AS (
    SELECT kit_id
    FROM vista_test.vist_ml_management_job_queue
    WHERE (locked_by IS NULL OR lock_time < CURRENT_TIMESTAMP - INTERVAL '10 minutes')
    AND kit_id NOT IN (
        SELECT kit_id FROM vistadb_test.vist_ml_management_job_log WHERE status IN ('running', 'complete')
    )
    ORDER BY crate_at ASC
    LIMIT 1
)
UPDATE vista_test.vist_ml_management_job_queue
SET locked_by = 'worker_id_123', lock_time = CURRENT_TIMESTAMP
WHERE kit_id = (SELECT kit_id FROM cte)
RETURNING kit_id, job_name, parameters;


UPDATE vista_test.vist_ml_management_job_queue
SET locked_by = NULL, lock_time = NULL
WHERE lock_time < CURRENT_TIMESTAMP - INTERVAL '10 minutes';