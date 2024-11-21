import asyncio
from typing import Annotated
from fastapi import Body, FastAPI
from openai import BaseModel

from src.infra.utiils.gracefully_shutdown import GracefulKiller
from src.domain.use_cases.entities.data_extraction_type import DataExtractionType
from job import TaskRunner, job


app = FastAPI()


class StartDataExtractionRequest(BaseModel):
    extractor_type: DataExtractionType
    months_before: int
    months_after: int


@app.post("/extractor")
async def start_robot(body: Annotated[StartDataExtractionRequest, Body()]):
    # TODO: implement the executions of the job coordinator
    asyncio.create_task(
        job(
            extractor_key=body.extractor_type,
            headless=True,
            months_before=body.months_before,
            months_after=body.months_after,
        )
    )
    return {"message": "Job Running"}


if __name__ == "__main__":
    import uvicorn

    runner = TaskRunner()
    runner.start()
    GracefulKiller([runner.stop])
    uvicorn.run("main:app")
