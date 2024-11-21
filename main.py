import asyncio
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Body, FastAPI
from openai import BaseModel

from job import TaskRunner, job
from src.domain.use_cases.entities.data_extraction_type import DataExtractionType


@asynccontextmanager
async def lifespan(app: FastAPI):
    runner = TaskRunner()
    runner.start()
    yield
    runner.stop()
    # GracefulKiller([runner.stop])


app = FastAPI(lifespan=lifespan)


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

    uvicorn.run("main:app", port=8083)
