import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, StrictStr


load_dotenv()


class ConfigModel(BaseModel):
    DEBUG: bool = Field(default=False)
    SHOWCASE_URL: StrictStr = Field(default="", pattern=r"^https?://.*")
    TIMELINE_URL: StrictStr = Field(default="", pattern=r"^https?://.*")
    IMAGES_FOLDER_PATH: StrictStr = Field(default="", min_length=3, max_length=255)
    DATABASE_HOST: StrictStr = Field(default="", min_length=3, max_length=255)
    DATABASE_NAME: StrictStr = Field(default="", min_length=3, max_length=255)
    DATABASE_USER: StrictStr = Field(default="", min_length=2, max_length=255)
    DATABASE_PASSWORD: StrictStr = Field(default="", min_length=3, max_length=255)
    DATABASE_PORT: int = Field(default=5432)


ConfigEnvs = ConfigModel(
    DEBUG=os.getenv("DEBUG", "False").lower() == "true",
    SHOWCASE_URL=os.getenv("SHOWCASE_URL", ""),
    TIMELINE_URL=os.getenv("TIMELINE_URL", ""),
    IMAGES_FOLDER_PATH=os.getenv("IMAGES_FOLDER_PATH", "images"),
    DATABASE_HOST=os.getenv("DATABASE_HOST", "localhost"),
    DATABASE_NAME=os.getenv("DATABASE_NAME", "postgres"),
    DATABASE_USER=os.getenv("DATABASE_USER", "postgres"),
    DATABASE_PASSWORD=os.getenv("DATABASE_PASSWORD", "postgres"),
    DATABASE_PORT=int(os.getenv("DATABASE_PORT", "5432")),
)
