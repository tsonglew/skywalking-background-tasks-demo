import asyncio
import logging
from fastapi import FastAPI, BackgroundTasks
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SkyWalking Background Tasks Demo")


async def background_sleep_task(task_id: str):
    """
    Background coroutine that sleeps for 10 seconds.
    This simulates a long-running background task.
    """
    start_time = datetime.now()
    logger.info(f"[{task_id}] Background task started at {start_time}")
    
    await asyncio.sleep(10)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"[{task_id}] Background task completed at {end_time} (duration: {duration}s)")


@app.get("/test")
async def test_endpoint(background_tasks: BackgroundTasks):
    """
    Create a new background coroutine which sleeps for 10 seconds,
    and return "ok" immediately without waiting for the task.
    """
    task_id = f"task-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}"
    
    # Add the background task
    background_tasks.add_task(background_sleep_task, task_id)
    
    logger.info(f"[{task_id}] Endpoint returning immediately")
    return "ok"


@app.get("/")
async def root():
    """
    Root endpoint for health check.
    """
    return {
        "message": "SkyWalking Background Tasks Demo",
        "endpoints": {
            "/test": "Creates a background task that sleeps for 10 seconds",
            "/": "This health check endpoint"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
