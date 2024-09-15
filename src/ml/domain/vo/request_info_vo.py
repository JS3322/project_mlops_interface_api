from pydantic import BaseModel

class RequestInfoVO(BaseModel):
    """
    요청 정보 VO로 유저에게 sandbox 환경에서 모델을 테스트 할 수 있는 환경을 제공하기 위한 정보를 담고 있음 (하위 dict 형태로 제공)
    """
    kit_name: str
    target_performance: float
    username: str
    email: str
    description: str
    data_info: dict