# 파일 시스템 감시 핸들러 클래스
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ModelDirectoryHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            model_name = os.path.basename(event.src_path)
            start_model_server(model_name)
    def on_modified(self, event):
        if event.is_directory:
            model_name = os.path.basename(event.src_path)
            # 기존 모델 서버 종료 (생략: 구현 필요)
            start_model_server(model_name)

# 파일 시스템 감시 시작 함수
def start_watcher():
    event_handler = ModelDirectoryHandler()
    observer = Observer()
    observer.schedule(event_handler, path=model_dir, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()