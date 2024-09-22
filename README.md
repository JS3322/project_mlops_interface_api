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
CREATE TABLE request_info (
    id SERIAL PRIMARY KEY,
    data JSONB
);
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

#### temp
- 1뎁스, 전처 상태값, 2뎁스 각 job의 상태값 3뎁스 job의 상세값
- 질문1
```
postgresq db에서 vistadb_test.mlops_totalstate_table 이라는 table을 생성하려 합니다. 
이 테이블은 데이터 수집 job, doe로 데이터 생성 job, ml에서 전처리, 스케일링, 학습, 테스트 job 기능과 optimize job까지 모든 job의
task 생성, 상태, 현재 순서를 저장하는 테이블 입니다.
예를 들어 kit_id가 1이 생성되면 데이터 수집 job을 하고, doe로 데이터 생성 job을 진행하며, 
ml의 전처리, 스케일링, 학습, 테스트와 optimize 각각 job을 저장하고 관리합니다.
많은 유저가 빈번하게 업데이트를 하고, lock을 피하기 위해서는 mlops_totlastate_table 의 빠른 insert와 update가 필요합니다.
그래서, 어떻게 테이블 설계를 하고 관리할지 질문합니다.
```
- jsonb 에 따라 다르지만 1억 건에 30gb - 40gb
```append-only 방식으로 insert
CREATE TABLE vistadb_test.mlops_totalstate_table (
    id BIGSERIAL PRIMARY KEY,
    kit_id INTEGER NOT NULL,
    job_type VARCHAR(50) NOT NULL,
    task_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    current_order INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_mlops_totalstate_kit_id ON vistadb_test.mlops_totalstate_table (kit_id);
CREATE INDEX idx_mlops_totalstate_created_at ON vistadb_test.mlops_totalstate_table (created_at);

SELECT DISTINCT ON (kit_id, job_type, task_name)
    kit_id, job_type, task_name, status, current_order, created_at, metadata
FROM vistadb_test.mlops_totalstate_table
WHERE kit_id = $1
ORDER BY kit_id, job_type, task_name, created_at DESC;
```

- 질문2
```
위 대답 토대로 mlops_totalstate_table 테이블과 함께 다음 요구사항으로 postgresq에 db table을 생성하려 합니다. oracle의 namespace과 같은 기능에서 이름은 vistadb_test 이고 다음과 같은 구조로 생성하니 create 문을 작성해주세요.
1. auto tdk 솔루션에서 deck이라는 데이터를 수집하는 python job id와 상태값을 관리하는 테이블이 필요합니다. request id라는 pk를 가집니다.
2. deck 데이터를 수집하면 머신러닝에서 사용할 데이터를 생성하기 위해 doe step을 진행하는 table이 필요합니다. job id와 함께, doe로 생성된 데이터 정보를 관리해야 합니다.
3. doe로 생성된 데이터를 기준으로 머신러닝 모델을 만들어야 합니다. ml 단계로써 전처리, 스케일링, 학습, 테스트 순서대로 진행하는 step 단계정보와 각 step의 state 정보와 job id 정보를 갖고 있어야 합니다.
4. 머신러닝 모델이 만들어지면 튜닝하는 optimize 단계를 관리하는 테이블이 필요합니다.
5. 생성된 table의 job들의 순서와 상태값과 id를 관리하는 테이블 mlops_totalstate_table을 고려하여 구성하시오.
```
```
-- 스키마 생성
CREATE SCHEMA IF NOT EXISTS vistadb_test;

-- 1. Deck 데이터 수집 테이블
CREATE TABLE vistadb_test.deck_collection (
    request_id SERIAL PRIMARY KEY,
    job_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- 2. DOE 단계 테이블
CREATE TABLE vistadb_test.doe_step (
    id SERIAL PRIMARY KEY,
    job_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL,
    data_info JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- 3. ML 단계 테이블
CREATE TABLE vistadb_test.ml_step (
    id SERIAL PRIMARY KEY,
    job_id UUID NOT NULL,
    step_name VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    step_order INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- 4. Optimize 단계 테이블
CREATE TABLE vistadb_test.optimize_step (
    id SERIAL PRIMARY KEY,
    job_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- 5. MLOPS 전체 상태 테이블
CREATE TABLE vistadb_test.mlops_totalstate_table (
    id BIGSERIAL PRIMARY KEY,
    kit_id INTEGER NOT NULL,
    job_type VARCHAR(50) NOT NULL,
    task_name VARCHAR(100) NOT NULL,
    job_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL,
    current_order INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- 인덱스 생성
CREATE INDEX idx_deck_collection_job_id ON vistadb_test.deck_collection (job_id);
CREATE INDEX idx_doe_step_job_id ON vistadb_test.doe_step (job_id);
CREATE INDEX idx_ml_step_job_id ON vistadb_test.ml_step (job_id);
CREATE INDEX idx_optimize_step_job_id ON vistadb_test.optimize_step (job_id);
CREATE INDEX idx_mlops_totalstate_kit_id ON vistadb_test.mlops_totalstate_table (kit_id);
CREATE INDEX idx_mlops_totalstate_job_id ON vistadb_test.mlops_totalstate_table (job_id);
CREATE INDEX idx_mlops_totalstate_job_type ON vistadb_test.mlops_totalstate_table (job_type);
CREATE INDEX idx_mlops_totalstate_status ON vistadb_test.mlops_totalstate_table (status);
```