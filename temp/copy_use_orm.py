# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@localhost/dbname")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
python
코드 복사
# models.py
from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class CopyJob(Base):
    __tablename__ = "copy_jobs"
    __table_args__ = {'schema': 'vista_test'}  # 스키마 지정

    id = Column(Integer, primary_key=True, index=True)
    source_path = Column(String, nullable=False)
    target_path = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    # 실패 여부를 추적하려면 다음과 같이 필드를 추가할 수 있습니다.
    # failed = Column(Boolean, default=False)
python
코드 복사
# schemas.py
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
from models import CopyJob
from schemas import CopyRequest
import os
import shutil
import logging
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)

def add_copy_jobs(db: Session, request: CopyRequest):
    """
    복사할 작업을 DB에 저장합니다.
    """
    for source in request.source_paths:
        # 파일 경로 검증 로직을 추가할 수 있습니다.
        job = CopyJob(
            source_path=source,
            target_path=request.target_path,
            completed=False
        )
        db.add(job)
    db.commit()

def execute_copy_jobs(db: Session):
    """
    DB에 저장된 복사 작업을 실행합니다.
    동시에 하나의 작업만 실행되도록 PostgreSQL Advisory Lock을 사용합니다.
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

        # 트랜잭션 시작
        with db.begin():
            # 완료되지 않은 작업 가져오기
            pending_jobs = db.query(CopyJob).filter(CopyJob.completed == False).all()

            if not pending_jobs:
                return {"message": "실행할 복사 작업이 없습니다."}

            for job in pending_jobs:
                try:
                    if os.path.isdir(job.source_path):
                        dest = os.path.join(job.target_path, os.path.basename(job.source_path))
                        shutil.copytree(job.source_path, dest, dirs_exist_ok=True)
                    else:
                        os.makedirs(job.target_path, exist_ok=True)
                        shutil.copy2(job.source_path, job.target_path)
                    # 작업 완료 표시
                    job.completed = True
                except Exception as e:
                    logging.error(f"{job.target_path}로 복사 중 오류 발생: {e}")
                    # 필요에 따라 작업 실패 표시
                    # job.failed = True
                    continue  # 다른 작업은 계속 진행

            # 모든 작업 상태를 커밋
            db.commit()

        return {"message": "복사 작업이 완료되었습니다."}
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
    add_copy_jobs(db, request)
    return {"message": "복사 작업이 DB에 저장되었습니다."}

@router.post("/execute_copy_jobs")
def execute_copy_jobs_endpoint(db: Session = Depends(get_db)):
    """
    복사 작업을 실행하는 엔드포인트입니다.
    """
    result = execute_copy_jobs(db)
    if "다른 복사 작업이 진행 중입니다." in result.get("message", ""):
        raise HTTPException(status_code=409, detail=result["message"])
    return result
python
코드 복사
# main.py
from fastapi import FastAPI
from controllers import router
from models import Base
from database import engine
from sqlalchemy import text

app = FastAPI()

# vista_test 스키마가 없을 경우 생성
with engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS vista_test;"))

# 테이블 생성
Base.metadata.create_all(bind=engine)

app.include_router(router)