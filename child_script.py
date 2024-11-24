import logging

# 하위 스크립트의 로거 설정
logger = logging.getLogger("child_script_logger")
logger.setLevel(logging.INFO)

# 간단한 로거 설정 (콘솔 출력만)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# 하위 스크립트 실행 시 로그 출력
logger.info("This is a logger message from the child script11.")
print("This is a print statement from the child script22.")
