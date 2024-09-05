import looging

route = APIRouter()
logger = logging.getLogger("default")

@route.post("/example")
def execute_sample():
    try:
    	data_list = [
        	{"name": "test1"},
            {"name": "test2"}
        ]
        return {"result":"success", "log":"test"}
    except Exception as e:
    	raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))