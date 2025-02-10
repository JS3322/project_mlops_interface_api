import os

def get_files_with_extension(folder_path, extension):
    """
    주어진 폴더에서 지정한 확장자를 가진 파일 목록을 반환합니다.
    
    Parameters:
        folder_path (str): 검색할 폴더의 경로.
        extension (str): 찾고자 하는 파일의 확장자 (예: '.txt' 또는 'txt').
        
    Returns:
        list: 확장자가 일치하는 파일들의 목록.
    """
    # 확장자가 '.'로 시작하지 않으면 추가합니다.
    if not extension.startswith('.'):
        extension = '.' + extension
    
    # 폴더 경로가 유효한지 확인합니다.
    if not os.path.isdir(folder_path):
        raise ValueError(f"유효하지 않은 폴더 경로: {folder_path}")
    
    file_list = []
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)
        # 파일인지 확인 후 확장자 검사
        if os.path.isfile(full_path) and filename.endswith(extension):
            file_list.append(filename)
    
    return file_list

# 사용 예시:
if __name__ == "__main__":
    folder = "/path/to/your/folder"  # 실제 폴더 경로로 변경하세요.
    ext = "txt"  # 또는 ".txt"
    try:
        txt_files = get_files_with_extension(folder, ext)
        print("찾은 파일 목록:")
        for file in txt_files:
            print(file)
    except ValueError as e:
        print(e)