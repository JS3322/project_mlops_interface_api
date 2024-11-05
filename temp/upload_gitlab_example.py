import gitlab
import os
import base64
import mimetypes

# 설정해야 할 변수들
GITLAB_URL = 'https://gitlab.com'  # 또는 여러분의 GitLab 인스턴스 URL
PRIVATE_TOKEN = 'your_personal_access_token'  # 개인 엑세스 토큰
PROJECT_ID = 'your_project_id_or_namespace/project_name'  # 프로젝트 ID 또는 경로
BRANCH_NAME = 'new_branch_name'  # 생성할 브랜치 이름
DIRECTORY_PATH = '/path/to/your/directory'  # 업로드할 디렉토리 경로

# GitLab에 인증
gl = gitlab.Gitlab(GITLAB_URL, private_token=PRIVATE_TOKEN)

# 프로젝트 가져오기
project = gl.projects.get(PROJECT_ID)

# 기본 브랜치로부터 새로운 브랜치 생성
default_branch = project.default_branch
project.branches.create({'branch': BRANCH_NAME, 'ref': default_branch})

# 커밋에 추가할 액션 준비
actions = []
for root, dirs, files in os.walk(DIRECTORY_PATH):
    for file in files:
        file_path = os.path.join(root, file)
        # 저장소 내의 파일 경로 계산
        rel_path = os.path.relpath(file_path, DIRECTORY_PATH)
        repo_file_path = rel_path.replace('\\', '/')  # Windows 호환성

        # 파일 내용 읽기
        with open(file_path, 'rb') as f:
            content = f.read()

        # 파일이 텍스트 파일인지 바이너리 파일인지 확인
        mime_type, encoding = mimetypes.guess_type(file_path)
        is_text = mime_type and mime_type.startswith('text/')

        if is_text:
            content_str = content.decode('utf-8', errors='replace')
            action = {
                'action': 'create',
                'file_path': repo_file_path,
                'content': content_str,
            }
        else:
            content_b64 = base64.b64encode(content).decode('utf-8')
            action = {
                'action': 'create',
                'file_path': repo_file_path,
                'content': content_b64,
                'encoding': 'base64',
            }

        actions.append(action)

# 모든 파일을 포함하는 커밋 생성
commit_data = {
    'branch': BRANCH_NAME,
    'commit_message': 'Add files from directory',
    'actions': actions,
}

project.commits.create(commit_data)

print(f"브랜치 '{BRANCH_NAME}'에 디렉토리 업로드가 완료되었습니다.")