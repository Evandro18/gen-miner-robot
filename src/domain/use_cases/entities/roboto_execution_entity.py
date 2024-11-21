from datetime import datetime
from typing import Optional
from openai import BaseModel
from pydantic import Extra, Field


class RobotExecutionEntity(BaseModel, extra="ignore"):
    robot_id: Optional[int] = Field(default=None)
    robot_name: str
    robot_status: str
    robot_start_time: datetime
    robot_end_time: Optional[datetime] = Field(default=None)
    robot_log: Optional[str] = Field(default=None)
