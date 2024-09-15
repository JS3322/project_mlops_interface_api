from fastapi import HTTPException, status, APIRouter, Depends
from src.ml.domain.vo.request_info_vo import RequestInfoVO
from fastapi.security import OAuth2PasswordBearer
from fastapi import BackgroundTasks
import logging
from src.common.di.example import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def write_log(message: str):
    with open("log.txt", mode="a") as log:
        log.write(message)

route = APIRouter()
logger = logging.getLogger("default")
# db=Depends(get_db)
# , token: str = Depends(oauth2_scheme)
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