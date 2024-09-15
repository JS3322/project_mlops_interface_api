#### todo
- 타 터미널에서 로그 확인
    ```
    uvicorn main:app --reload > fastapi.log 2>&1 &
    tail -f /var/log/application.log
    strace -p [프로세스 ID] -e trace=write
    ```
---
#### TEST case

### 빈번한 db 업데이트와 캐시 이슈 예상
```
1. Cache-Aside Pattern 또는 버전 기반 캐시 업데이트
2. 캐시 미스 발생 시, 데이터베이스에서 데이터를 가져오고 캐시를 업데이트
3. 캐시 미스가 발생하지 않을 경우, 캐시에서 데이터를 가져옴
```



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
