import os
import subprocess

def create_and_set_permissions(base_dir, folder_name, group_name):
    """
    지정된 디렉토리를 생성하고 그룹 쓰기 및 수정 권한을 설정합니다.
    
    :param base_dir: 생성할 디렉토리의 부모 디렉토리 경로
    :param folder_name: 생성할 디렉토리 이름
    :param group_name: 디렉토리에 권한을 부여할 그룹 이름
    """
    # 디렉토리 경로 설정
    folder_path = os.path.join(base_dir, folder_name)
    
    try:
        # 디렉토리 생성
        os.makedirs(folder_path, exist_ok=True)
        print(f"폴더 생성됨: {folder_path}")
        
        # 그룹 변경
        subprocess.run(["chgrp", group_name, folder_path], check=True)
        print(f"폴더의 그룹 소유권 설정됨: {group_name}")
        
        # 권한 설정 (rwxrwx---: 그룹에게 쓰기 및 수정 권한 부여)
        subprocess.run(["chmod", "2770", folder_path], check=True)
        print(f"폴더 권한 설정됨: rwxrws--- (Group write and modify enabled)")
        
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    # 기본 디렉토리
    base_directory = "/home/viststorage2"
    
    # 폴더 이름들
    user_folders = ["viststorage", "caev13784", "bbb123"]
    
    # 그룹 이름
    group_account = "viststorage2"
    
    # 각 폴더에 대해 권한 설정
    for folder in user_folders:
        create_and_set_permissions(base_directory, folder, group_account)