from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import psycopg2
from psycopg2.extras import Json

# PostgreSQL 연결 설정
DB_CONFIG = {
    "dbname": "your_db",
    "user": "your_user",
    "password": "your_password",
    "host": "localhost",
    "port": 5432,
}

app = FastAPI()

# Job 요청 데이터 모델
class JobRequest(BaseModel):
    job_type: str
    parameters: dict

# DB 연결 함수
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# Job 추가 API
@app.post("/add-job")
def add_job(job_request: JobRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Job 추가 SQL
        job_query = """
        INSERT INTO job_queue (job_type, parameters, created_at)
        VALUES (%s, %s, NOW()) RETURNING id;
        """
        cursor.execute(job_query, (job_request.job_type, Json(job_request.parameters)))
        job_id = cursor.fetchone()[0]

        # 상태 기록 SQL
        status_query = """
        INSERT INTO job_status_log (job_id, status, updated_at)
        VALUES (%s, %s, NOW());
        """
        cursor.execute(status_query, (job_id, "pending"))

        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Job added", "job_id": job_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Job 상태 확인 API
@app.get("/job-status/{job_id}")
def get_job_status(job_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Job 상태 조회 SQL
        query = """
        SELECT status, updated_at FROM job_status_log
        WHERE job_id = %s
        ORDER BY updated_at DESC
        LIMIT 1;
        """
        cursor.execute(query, (job_id,))
        status = cursor.fetchone()

        cursor.close()
        conn.close()

        if status:
            return {"job_id": job_id, "status": status[0], "updated_at": status[1]}
        else:
            raise HTTPException(status_code=404, detail="Job not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))