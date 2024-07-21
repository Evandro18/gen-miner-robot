import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, StrictStr


load_dotenv()

class ConfigModel(BaseModel):
    DEBUG: bool = Field(default=False)
    SHOWCASE_URL: StrictStr = Field(default='', pattern=r'^https?://.*')
    TIMELINE_URL: StrictStr = Field(default='', pattern=r'^https?://.*')
    IMAGES_FOLDER_PATH: StrictStr = Field(default='', min_length=3, max_length=255)
    DOCUMENTS_FOLDER_PATH: StrictStr = Field(default='', min_length=3, max_length=255)
    

ConfigEnvs = ConfigModel(
    DEBUG=os.getenv('DEBUG', 'False').lower() == 'true',
    SHOWCASE_URL=os.getenv('SHOWCASE_URL', ''),
    TIMELINE_URL=os.getenv('TIMELINE_URL', ''),
    IMAGES_FOLDER_PATH=os.getenv('IMAGES_FOLDER_PATH', 'images'),
    DOCUMENTS_FOLDER_PATH=os.getenv('DOCUMENTS_FOLDER_PATH', 'images')
)
    
    