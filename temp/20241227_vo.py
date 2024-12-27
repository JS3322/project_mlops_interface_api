# vo.py
from pydantic import BaseModel
from typing import Optional

class ModelVO(BaseModel):
    model_name: str
    model_activation: bool
    last_execution_time: str  # 간단히 str로 처리 (날짜/시각 포맷)
    pid: int
    description: Optional[str] = None