import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

class ConfigEnv(BaseModel):
    FASTAPI_DEBUG: bool = Field(default=False)

envs_names = ['FASTAPI_DEBUG']
envs = {env_name: (os.getenv(env_name) or '') for env_name in envs_names}

Envs = ConfigEnv(
    FASTAPI_DEBUG=bool(envs['FASTAPI_DEBUG'])
)
