from fastapi import HTTPException, status, APIRouter
from src.ml.domain.vo.request_info_vo import RequestInfoVO
import logging

route = APIRouter()
logger = logging.getLogger("default")

@route.post("/example")
def execute_sample(request_info: RequestInfoVO):
    try:
        # 로그에 요청 정보 기록
        logger.info(f"Received request: {request_info}")

        # 요청 정보를 JSON 형식으로 변환
        request_data = request_info.dict()

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