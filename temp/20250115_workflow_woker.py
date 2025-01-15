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