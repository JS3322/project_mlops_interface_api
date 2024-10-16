from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import shutil
import os

# 데이터베이스 설정
DATABASE_URL = "postgresql+psycopg2://user:password@localhost/mydatabase"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ORM 모델
class CopyQueue(Base):
    __tablename__ = "copy_queue"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, unique=True, index=True)
    target_path = Column(String)  # target_path 필드
    items = relationship("CopyQueueItem", back_populates="copy_queue", cascade="all, delete-orphan")

class CopyQueueItem(Base):
    __tablename__ = "copy_queue_item"
    id = Column(Integer, primary_key=True, index=True)
    copy_queue_id = Column(Integer, ForeignKey("copy_queue.id"))
    path = Column(String)
    copy_queue = relationship("CopyQueue", back_populates="items")

# 테이블 생성
Base.metadata.create_all(bind=engine)

# Pydantic 모델
class CopyRequest(BaseModel):
    paths: List[str]  # 복사할 파일 및 디렉토리의 경로 리스트
    target_path: str  # 복사할 대상 경로

# FastAPI 앱 초기화
app = FastAPI()

# 복사 작업을 큐에 추가하는 API 엔드포인트
@app.post("/add_to_copy_queue/{task_id}")
def add_to_copy_queue(task_id: int, request: CopyRequest):
    db = SessionLocal()
    try:
        # 기존에 동일한 task_id가 있는지 확인하고 없으면 생성
        copy_queue = db.query(CopyQueue).filter(CopyQueue.task_id == task_id).first()
        if not copy_queue:
            copy_queue = CopyQueue(task_id=task_id, target_path=request.target_path)
            db.add(copy_queue)
            db.flush()  # id 값을 얻기 위해 flush 호출
        else:
            # 기존 copy_queue의 target_path 업데이트
            copy_queue.target_path = request.target_path

        # 기존 아이템 삭제
        db.query(CopyQueueItem).filter(CopyQueueItem.copy_queue_id == copy_queue.id).delete()

        # 새로운 아이템 추가
        items = [CopyQueueItem(path=path, copy_queue=copy_queue) for path in request.paths]
        db.add_all(items)
        db.commit()
        return {"message": f"작업 {task_id}의 복사 큐가 업데이트되었습니다"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# 복사 프로세스를 실행하는 API 엔드포인트 (task_id 제거)
@app.post("/execute_copy")
def execute_copy():
    db = SessionLocal()
    try:
        # 글로벌 어드바이저리 락 획득 시도 (고정된 키 값 사용)
        result = db.execute("SELECT pg_try_advisory_lock(9999);")  # 9999는 임의의 고정 키 값
        acquired = result.fetchone()[0]
        if not acquired:
            raise HTTPException(status_code=400, detail="복사 프로세스가 이미 실행 중입니다")

        # 복사 프로세스 수행
        copy_process(db)
        return {"message": "복사 프로세스가 완료되었습니다"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 어드바이저리 락 해제
        db.execute("SELECT pg_advisory_unlock(9999);")
        db.close()

# 모든 작업에 대한 복사 프로세스 함수
def copy_process(db):
    try:
        copy_queues = db.query(CopyQueue).all()
        if not copy_queues:
            print("복사할 작업이 없습니다.")
            return

        for copy_queue in copy_queues:
            task_id = copy_queue.task_id
            target_dir = copy_queue.target_path

            print(f"작업 {task_id}의 복사를 시작합니다.")

            for item in copy_queue.items:
                path = item.path
                try:
                    if os.path.isdir(path):
                        dest_dir = os.path.join(target_dir, os.path.basename(path))
                        shutil.copytree(path, dest_dir, dirs_exist_ok=True)
                    elif os.path.isfile(path):
                        shutil.copy2(path, target_dir)
                    else:
                        print(f"경로를 찾을 수 없습니다: {path}")
                except Exception as e:
                    print(f"작업 {task_id}에서 경로 {path} 복사 중 오류 발생: {e}")

            # 복사 후 해당 작업 삭제
            db.delete(copy_queue)
            db.commit()

            print(f"작업 {task_id}의 복사가 완료되었습니다.")
    except Exception as e:
        print(f"복사 중 오류 발생: {e}")
        db.rollback()
        raise