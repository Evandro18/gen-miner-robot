import asyncio
from fastapi import FastAPI, Request


app = FastAPI()


@app.get("/hello")
async def start_robot(request: Request):
    # asyncio.run(
    #     Main(
    #         extractor_key=DataExtractionType.BATCHES,
    #         headless=True,
    #         months_before=0,
    #         months_after=0,
    #     )
    # )
    return {"message": "Job Running"}


import uvicorn

if __name__ == "__main__":
    uvicorn.run("server:app", reload=True)
