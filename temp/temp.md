* 관리 포인트 논의사항
    * path 관리 주체 정리 및 공통코드 정리
    * path 관련 정보 공통화 : shell, java, python 각각 path 관리를 공통화 논의 필요 (공통 환경변수 중앙 관리화)



=CREATE TABLE workflow_definitions (
    workflow_id SERIAL PRIMARY KEY,
    workflow_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE workflow_steps (
    step_id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL REFERENCES workflow_definitions(workflow_id) ON DELETE CASCADE,
    step_name VARCHAR(100) NOT NULL,
    task_code VARCHAR(50) NOT NULL, -- common_codes 테이블의 code_key 참조
    parent_step_id INTEGER REFERENCES workflow_steps(step_id) ON DELETE SET NULL,
    condition VARCHAR(255), -- 선택적: 분기 조건을 정의할 수 있음
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (workflow_id, step_name)
);




CREATE TABLE common_codes (
    code_id VARCHAR(20) PRIMARY KEY,
    code_type VARCHAR(50) NOT NULL,
    code_key VARCHAR(50) NOT NULL,
    code_value VARCHAR(255),
    description TEXT,
    UNIQUE (code_type, code_key)
);

-- Step 1: 데이터 전처리
INSERT INTO workflow_steps (workflow_id, step_name, task_code, parent_step_id) VALUES
(1, 'Data Preprocessing', 'DATA_PREPROCESSING', NULL);

-- Step 2: 학습
INSERT INTO workflow_steps (workflow_id, step_name, task_code, parent_step_id) VALUES
(1, 'Model Training', 'TRAINING', 1);

-- Step 3: 테스트
INSERT INTO workflow_steps (workflow_id, step_name, task_code, parent_step_id) VALUES
(1, 'Model Testing', 'TESTING', 2);

-- Step 4: 서빙
INSERT INTO workflow_steps (workflow_id, step_name, task_code, parent_step_id, condition) VALUES
(1, 'Model Serving', 'SERVING', 3, 'accuracy >= 0.9');

-- Step 5: 모델 파인튜닝
INSERT INTO workflow_steps (workflow_id, step_name, task_code, parent_step_id, condition) VALUES
(1, 'Model Fine-tuning', 'FINE_TUNING', 3, 'accuracy < 0.9');

-- Step 6: 옵티마이저 설정 (예시 추가)
INSERT INTO workflow_steps (workflow_id, step_name, task_code, parent_step_id) VALUES
(1, 'Optimizer Adjustment', 'OPTIMIZER_SETTING', 3);
