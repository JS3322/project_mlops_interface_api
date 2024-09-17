from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON
import json
from src.common.di.example import get_db
from src.ml.domain.vo.request_info_vo import RequestInfoVO

Base = declarative_base()

class RequestInfo(Base):
    __tablename__ = "request_info"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(String)

def insert_request_info(request_info: RequestInfoVO, db: Session = Depends(get_db)):
    json_data = json.dumps(request_info.dict())
    db_item = RequestInfo(data=json_data)
    
    # Get a database session
    db = next(get_db())
    
    db.add(db_item)
    
    db.commit()
    db.refresh(db_item)
    return db_item.id

def read_request_info(item_id: int, db: Session = Depends(get_db)) -> dict:
    # Get a database session
    db = next(get_db()) 
    
    db_item = db.query(RequestInfo).filter(RequestInfo.id == item_id).first()
    if db_item:
        return db_item.data
    return None
