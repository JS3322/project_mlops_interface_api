import os

def create_directory():
    HOME_PATH = os.path.dirname(os.getcwd())
    new_directory_path = os.path.join(HOME_PATH, 'USER_NAME', 'DATE')
    os.makedirs(new_directory_path, exist_ok=True)
    return new_directory_path
