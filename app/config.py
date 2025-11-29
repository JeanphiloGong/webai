"""
配置文件
"""
import os
from pathlib import Path
from dotenv import load_dotenv

########################################
# 根目录
#######################################

ROOT_DIR = Path(__file__).resolve().parent

######################
# ENV 文件
#######################

ENV_PATH = ROOT_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

ENV_EXIST = os.getenv("ENV_FILE")

if ENV_EXIST:
    print("环境变量加载成功")
else:
    print("环境变量加载失败")


#################
# DATABASE
#################

DATABASE_USER = os.environ.get("DATABASE_USER", "webai_user")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD", "Jeanphilo..")
DATABASE_PORT = os.environ.get("DATABASE_PORT", "5432")
DATABASE_HOST = os.environ.get("DATABASE_HOST", "localhost")

####################
# JWT
###################
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", 'dev-secret-key')
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


