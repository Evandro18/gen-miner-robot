from typing import Optional
from src.domain.use_cases.entities.roboto_execution_entity import RobotExecutionEntity
from src.infra.repositories.sqlserver.database import Base, Database
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey


class RobotExecution(Base):
    __tablename__ = "robot_execution"

    robot_id = Column(Integer, primary_key=True, autoincrement=True)
    robot_name = Column(String)
    robot_status = Column(String)
    robot_start_time = Column(DateTime)
    robot_end_time = Column(DateTime, nullable=True)
    robot_log = Column(String, nullable=True)


class RobotExecutionRepository:
    def __init__(self, db: Database):
        self.db = db

    def insert(self, robot_execution: RobotExecutionEntity) -> RobotExecutionEntity:
        session = self.db.get_session()
        model = RobotExecution(**robot_execution.model_dump())
        session.add(model)
        session.commit()
        session.refresh(model)
        return RobotExecutionEntity(**model.__dict__)

    def get(self, robot_id: int) -> RobotExecutionEntity:
        session = self.db.get_session()
        model = (
            session.query(RobotExecution)
            .filter(RobotExecution.robot_id == robot_id)
            .first()
        )
        return RobotExecutionEntity(**model.__dict__)

    def update(self, robot_execution: RobotExecutionEntity) -> RobotExecutionEntity:
        session = self.db.get_session()
        if robot_execution.robot_id is None:
            raise ValueError("Robot id is required")

        robot_id = int(robot_execution.robot_id)
        del robot_execution.robot_id
        model = (
            session.query(RobotExecution)
            .filter(RobotExecution.robot_id == robot_id)
            .update({**robot_execution.model_dump()})
        )

        session.commit()
        result = (
            session.query(RobotExecution)
            .filter(RobotExecution.robot_id == robot_id)
            .first()
        )

        return RobotExecutionEntity(**result.__dict__)

    def filterByStatus(self, status: str) -> Optional[RobotExecutionEntity]:
        session = self.db.get_session()
        model = (
            session.query(RobotExecution)
            .filter(RobotExecution.robot_status == status)
            .first()
        )

        if model is None:
            return None

        return RobotExecutionEntity(**model.__dict__)
