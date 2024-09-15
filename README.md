#### todo
- 타 터미널에서 로그 확인
    ```
    uvicorn main:app --reload > fastapi.log 2>&1 &
    tail -f /var/log/application.log
    strace -p [프로세스 ID] -e trace=write
    ```
---
#### TEST case





```
source ./.venv/bin/activate
```

```bash
uvicorn ./main_v0.0.1:app --reload
```
```
http://127.0.0.1:8000/redoc
```
```
http://127.0.0.1:8000/docs
```
---
#### Sturuct
