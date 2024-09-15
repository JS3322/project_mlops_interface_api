from dotenv import load_dotenv
import os

class Settings:
    HOME_PATH=""
    
    @staticmethod
    def load_enviroment_config():
        env = 'default'
        dotenv_path = f".env.{env}"
        load_dotenv(dotenv_path)
        
        Settings.HOME_PATH = os.getenv("HOME_PATH")
        
    Settings.load_enviroment_config()