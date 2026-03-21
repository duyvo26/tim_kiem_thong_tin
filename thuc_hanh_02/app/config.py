import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # BASE
    DIR_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # API SETTINGS
    TITLE_APP = os.environ.get("TITLE_APP", "GooSearch API")
    VERSION_APP = os.environ.get("VERSION_APP", "v1")
    ALLOW_ORIGINS = os.environ.get("ALLOW_ORIGINS", "*")
    
    # SEARCH ENGINE PATHS
    DATASET_DIR = os.path.join(DIR_ROOT, "dataset")
    STORAGE_DIR = DIR_ROOT # Nơi lưu index (.txt)
    STOPWORDS_PATH = os.path.join(DIR_ROOT, "vietnamese-stopwords.txt")
    
    # VNCORENLP & JAVA
    VNCORENLP_DIR = os.environ.get("VNCORENLP_DIR", os.path.join(DIR_ROOT, "vncorenlp"))
    JAVA_HOME = os.environ.get("JAVA_HOME", r"C:\Program Files\Java\jdk1.8.0_202")

settings = Settings()
