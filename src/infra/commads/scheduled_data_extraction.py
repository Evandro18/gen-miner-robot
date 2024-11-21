from datetime import datetime
from src.domain.ports.extractors import ExtractorExtraParameters
from src.domain.use_cases.entities.roboto_execution_entity import RobotExecutionEntity
from src.infra.core.logging import Log
from src.infra.repositories.sqlserver.robot_execution_repository import (
    RobotExecutionRepository,
)
from src.domain.use_cases.entities.data_extraction_type import DataExtractionType
from src.domain.use_cases.process_auction_data_extraction_use_case import (
    ProcessAuctionDataExtractionUseCase,
)


class ScheduledDataExtraction:
    def __init__(
        self,
        data_extraction_service: ProcessAuctionDataExtractionUseCase,
        robot_execution_repository: RobotExecutionRepository,
    ):
        self._data_extraction_service = data_extraction_service
        self._robot_execution_repository = robot_execution_repository

    async def run(
        self, type: DataExtractionType, extra_params: ExtractorExtraParameters
    ) -> bool:
        try:
            exists = self._robot_execution_repository.filterByStatus("RUNNING")
            if exists is not None:
                Log.info(
                    "There is a robot execution running, so this execution will be ignored"
                )
                return False

            robot_execution = RobotExecutionEntity(
                robot_name=type,
                robot_status="RUNNING",
                robot_start_time=datetime.now(),
            )

            robot_execution = self._robot_execution_repository.insert(robot_execution)

            failed_batches = await self._data_extraction_service.execute(
                type=type, extra_params=extra_params
            )

            robot_execution.robot_status = "SUCCESS"
            robot_execution.robot_end_time = datetime.now()
            if len(failed_batches) > 0:
                robot_execution.robot_log = (
                    f"Failed batches: {','.join(failed_batches)}"
                )

            self._robot_execution_repository.update(robot_execution)
            return True
        except Exception as e:
            Log.error(f"Error on GetAuctionBatchesUseCase: {e}")
            if robot_execution is not None:
                robot_execution.robot_status = "ERROR"
                robot_execution.robot_log = str(e)
                self._robot_execution_repository.update(robot_execution)
            return False
