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




### 구조

- 다음과 같은 구조로 테스트 케이스를 작성합니다
---

#### 요구사항 목록
| 요구사항 ID | 요구사항 설명 |
|-------------|----------------|
| REQ-001 | SSO 로그인한 유저는 본 솔루션에 권한 신청을 할 수 있어야 한다. |
| REQ-002 | 유저는 logic 일반권한, logic 모델셋업권한, dram 일반권한을 신청할 수 있어야 한다. |
| REQ-003 | 모델셋업 권한자는 머신러닝 모델을 복사하여 사용할 모델을 셋업할 수 있어야 한다. |
| REQ-004 | 일반권한 유저는 셋업한 모델에 대해 권한 신청을 하여 사용 권한을 획득할 수 있어야 한다. |
| REQ-005 | 일반권한 유저는 lot tracking 시스템에서 필요한 row를 추가할 수 있어야 한다. |
| REQ-006 | 할당이 완료되면 매일 배치 작업이 돌아서 결과 데이터를 DB에 저장해야 한다. |

---

#### 테스트 케이스
| 테스트 케이스 ID | 요구사항 ID | 입력 값 | 예상 출력 | 설명 |
|-------------------|-------------|---------|------------|------|
| TC-001 | REQ-001 | 유효한 SSO 로그인 정보 | 권한 신청 페이지 접근 가능 | 유효한 SSO 로그인 정보를 가진 유저가 권한 신청 페이지에 접근할 수 있는지 확인 |
| TC-002 | REQ-001 | 유효하지 않은 SSO 로그인 정보 | 권한 신청 페이지 접근 불가 | 유효하지 않은 SSO 로그인 정보를 가진 유저가 권한 신청 페이지에 접근할 수 없는지 확인 |
| TC-003 | REQ-001 | SSO 로그인 후 세션 만료 | 권한 신청 페이지 접근 불가 | SSO 로그인 후 세션이 만료된 경우 권한 신청 페이지에 접근할 수 없는지 확인 |
| TC-004 | REQ-001 | SSO 로그인 정보 없이 접근 시도 | 권한 신청 페이지 접근 불가 | SSO 로그인 정보 없이 권한 신청 페이지에 접근할 경우 접근할 수 없는지 확인 |
| TC-005 | REQ-001 | SSO 로그인 후 권한 신청 버튼 클릭 | 권한 신청 페이지로 리디렉션 | SSO 로그인 후 권한 신청 버튼을 클릭했을 때 권한 신청 페이지로 리디렉션되는지 확인 |
| TC-001 | REQ-002 | 신청 권한: logic 일반권한 | 신청 성공 메시지 | 유저가 logic 일반권한을 신청했을 때 성공 메시지가 출력되는지 확인 |
| TC-002 | REQ-002 | 신청 권한: logic 모델셋업권한 | 신청 성공 메시지 | 유저가 logic 모델셋업권한을 신청했을 때 성공 메시지가 출력되는지 확인 |
| TC-003 | REQ-002 | 신청 권한: dram 일반권한 | 신청 성공 메시지 | 유저가 dram 일반권한을 신청했을 때 성공 메시지가 출력되는지 확인 |
| TC-004 | REQ-002 | 신청 권한: 잘못된 권한 | 오류 메시지 | 유저가 잘못된 권한을 신청했을 때 오류 메시지가 출력되는지 확인 |
| TC-005 | REQ-002 | 권한 신청 없이 제출 | 오류 메시지 | 유저가 권한 신청 없이 제출했을 때 오류 메시지가 출력되는지 확인 |
| TC-001 | REQ-003 | 모델셋업 권한자 로그인, 원본 모델 정보 | 모델 복사 성공 메시지 | 모델셋업 권한자가 원본 모델을 성공적으로 복사했을 때의 메시지를 확인 |
| TC-002 | REQ-003 | 모델셋업 권한자 로그인, 존재하지 않는 모델 정보 | 오류 메시지 | 모델셋업 권한자가 존재하지 않는 모델을 복사하려 할 때 오류 메시지가 출력되는지 확인 |
| TC-003 | REQ-003 | 모델셋업 권한자 로그인, 복사할 모델의 속성 변경 | 모델 복사 성공 메시지 | 모델셋업 권한자가 복사할 모델의 속성을 변경한 후 성공적으로 복사했을 때의 메시지를 확인 |
| TC-004 | REQ-003 | 모델셋업 권한자 로그인, 복사할 모델의 권한 부족 | 권한 부족 오류 메시지 | 모델셋업 권한자가 권한이 없는 모델을 복사하려 할 때 권한 부족 오류 메시지가 출력되는지 확인 |
| TC-005 | REQ-003 | 모델셋업 권한자 로그인, 복사 후 모델 확인 | 복사된 모델 정보 | 모델셋업 권한자가 복사한 모델이 데이터베이스에 존재하는지 확인 |
| TC-001 | REQ-004 | 일반권한 유저, 셋업된 모델 정보 | 권한 신청 성공 메시지 | 일반권한 유저가 셋업된 모델에 대해 권한 신청을 했을 때 성공 메시지가 출력되는지 확인 |
| TC-002 | REQ-004 | 일반권한 유저, 권한 신청 시 필요한 정보 누락 | 오류 메시지 | 일반권한 유저가 권한 신청 시 필요한 정보를 누락했을 때 오류 메시지가 출력되는지 확인 |
| TC-003 | REQ-004 | 일반권한 유저, 권한 신청 후 승인 대기 상태 | 승인 대기 메시지 | 일반권한 유저가 권한 신청 후 승인 대기 상태로 전환되는지 확인 |
| TC-004 | REQ-004 | 일반권한 유저, 권한 신청 후 거부 상태 | 거부 메시지 | 일반권한 유저가 권한 신청 후 거부되었을 때 거부 메시지가 출력되는지 확인 |
| TC-005 | REQ-004 | 일반권한 유저, 이미 권한을 가진 모델에 대한 신청 | 이미 권한 보유 메시지 | 일반권한 유저가 이미 권한을 가진 모델에 대해 다시 권한 신청을 했을 때 메시지가 출력되는지 확인 |
| TC-001 | REQ-005 | 일반권한 유저, 추가할 row 정보 | 추가 성공 메시지 | 일반권한 유저가 lot tracking 시스템에 row를 추가했을 때 성공 메시지가 출력되는지 확인 |
| TC-002 | REQ-005 | 일반권한 유저, 필수 정보 누락 | 오류 메시지 | 일반권한 유저가 row 추가 시 필수 정보를 누락했을 때 오류 메시지가 출력되는지 확인 |
| TC-003 | REQ-005 | 일반권한 유저, 중복된 row 추가 시도 | 오류 메시지 | 일반권한 유저가 이미 존재하는 row를 추가하려 할 때 오류 메시지가 출력되는지 확인 |
| TC-004 | REQ-005 | 일반권한 유저, 유효하지 않은 데이터 형식 | 오류 메시지 | 일반권한 유저가 유효하지 않은 데이터 형식으로 row를 추가하려 할 때 오류 메시지가 출력되는지 확인 |
| TC-005 | REQ-005 | 일반권한 유저, 추가 후 데이터 확인 | 추가된 row 정보 | 일반권한 유저가 추가한 row가 lot tracking 시스템에 존재하는지 확인 |
| TC-006 | REQ-006 | 배치 작업 트리거 | DB에 결과 데이터 저장 | 배치 작업이 매일 돌아서 DB에 결과 데이터를 저장하는지 확인 |

---
