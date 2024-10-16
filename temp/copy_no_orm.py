python
코드 복사
# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 환경 변수로부터 데이터베이스 URL을 가져옵니다.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@localhost/dbname")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
python
코드 복사
# schemas.py (VO)
from pydantic import BaseModel
from typing import List

class CopyRequest(BaseModel):
    source_paths: List[str]
    target_path: str

    class Config:
        anystr_strip_whitespace = True
python
코드 복사
# services.py
from sqlalchemy.orm import Session
from schemas import CopyRequest
import os
import shutil
import logging
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)

def add_copy_jobs(db: Session, request: CopyRequest):
    """
    복사할 작업을 데이터베이스에 저장합니다.
    """
    insert_sql = text("""
        INSERT INTO vista_test.copy_jobs (source_path, target_path, completed)
        VALUES (:source_path, :target_path, FALSE)
    """)

    data = [
        {'source_path': source, 'target_path': request.target_path}
        for source in request.source_paths
    ]

    try:
        db.execute(insert_sql, data)
        db.commit()
    except Exception as e:
        db.rollback()
        logging.error(f"복사 작업 추가 중 오류 발생: {e}")
        raise

def execute_copy_jobs(db: Session):
    """
    저장된 복사 작업을 실행합니다.
    PostgreSQL Advisory Lock을 사용하여 동시에 하나의 작업만 실행되도록 합니다.
    """
    lock_id = 12345  # 임의의 락 ID
    acquired = False

    try:
        # Advisory Lock 획득 시도
        acquired = db.execute(
            text("SELECT pg_try_advisory_lock(:id)"),
            {"id": lock_id}
        ).scalar()

        if not acquired:
            return {"message": "다른 복사 작업이 진행 중입니다."}

        # 완료되지 않은 작업 가져오기
        select_sql = text("""
            SELECT id, source_path, target_path FROM vista_test.copy_jobs
            WHERE completed = FALSE
        """)
        pending_jobs = db.execute(select_sql).fetchall()

        if not pending_jobs:
            return {"message": "실행할 복사 작업이 없습니다."}

        for job in pending_jobs:
            job_id = job.id
            source_path = job.source_path
            target_path = job.target_path
            try:
                # 파일 경로 검증 (필요에 따라 추가)
                if os.path.isdir(source_path):
                    dest = os.path.join(target_path, os.path.basename(source_path))
                    shutil.copytree(source_path, dest, dirs_exist_ok=True)
                else:
                    os.makedirs(target_path, exist_ok=True)
                    shutil.copy2(source_path, target_path)

                # 작업 완료 표시
                update_sql = text("""
                    UPDATE vista_test.copy_jobs SET completed = TRUE WHERE id = :id
                """)
                db.execute(update_sql, {'id': job_id})
            except Exception as e:
                logging.error(f"{target_path}로 복사 중 오류 발생: {e}")
                # 필요한 경우 작업 실패로 표시하거나 로그에 기록
                continue  # 다른 작업은 계속 진행

        db.commit()
        return {"message": "복사 작업이 완료되었습니다."}
    except Exception as e:
        db.rollback()
        logging.error(f"복사 작업 실행 중 오류 발생: {e}")
        raise
    finally:
        if acquired:
            # Advisory Lock 해제
            db.execute(
                text("SELECT pg_advisory_unlock(:id)"),
                {"id": lock_id}
            )
            db.commit()
python
코드 복사
# controllers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import CopyRequest
from services import add_copy_jobs, execute_copy_jobs
from database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/add_copy_jobs")
def add_copy_jobs_endpoint(request: CopyRequest, db: Session = Depends(get_db)):
    """
    복사 작업을 추가하는 엔드포인트입니다.
    """
    try:
        add_copy_jobs(db, request)
        return {"message": "복사 작업이 DB에 저장되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute_copy_jobs")
def execute_copy_jobs_endpoint(db: Session = Depends(get_db)):
    """
    복사 작업을 실행하는 엔드포인트입니다.
    """
    try:
        result = execute_copy_jobs(db)
        if "다른 복사 작업이 진행 중입니다." in result.get("message", ""):
            raise HTTPException(status_code=409, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
python
코드 복사
# main.py
from fastapi import FastAPI
from controllers import router
from database import engine
from sqlalchemy import text
import logging

app = FastAPI()

def init_db():
    """
    데이터베이스 초기화: 스키마 및 테이블 생성
    """
    with engine.connect() as conn:
        try:
            # 스키마 생성
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS vista_test;"))

            # 테이블 생성
            create_table_sql = text("""
            CREATE TABLE IF NOT EXISTS vista_test.copy_jobs (
                id SERIAL PRIMARY KEY,
                source_path TEXT NOT NULL,
                target_path TEXT NOT NULL,
                completed BOOLEAN DEFAULT FALSE
            );
            """)
            conn.execute(create_table_sql)
        except Exception as e:
            logging.error(f"데이터베이스 초기화 중 오류 발생: {e}")
            raise

# 데이터베이스 초기화
init_db()

# 라우터 추가
app.include_router(router)