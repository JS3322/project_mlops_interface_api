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