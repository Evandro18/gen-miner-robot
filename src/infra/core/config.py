import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

class ConfigEnv(BaseModel):
    DEBUG: bool = Field(default=False)

envs_names = ['DEBUG']
envs = {env_name: (os.getenv(env_name) or '') for env_name in envs_names}

Envs = ConfigEnv(
    DEBUG=bool(envs['DEBUG'])
)
