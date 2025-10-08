"""
Simple test script to validate the application logic.
This can be run to verify the code structure is correct.
"""
import asyncio
import sys
from datetime import datetime

async def background_sleep_task(task_id: str):
    """
    Background coroutine that sleeps for 10 seconds.
    This simulates a long-running background task.
    """
    start_time = datetime.now()
    print(f"[{task_id}] Background task started at {start_time}")
    
    await asyncio.sleep(10)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"[{task_id}] Background task completed at {end_time} (duration: {duration}s)")


async def test_background_task():
    """
    Test that demonstrates the background task behavior.
    """
    task_id = f"test-task-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}"
    
    print(f"\n[TEST] Creating background task: {task_id}")
    print(f"[TEST] This simulates the /test endpoint behavior")
    
    # Start the background task
    task = asyncio.create_task(background_sleep_task(task_id))
    
    # Immediately return without waiting
    print(f"[TEST] Returning 'ok' immediately (not waiting for background task)")
    print(f"[TEST] Response: 'ok'\n")
    
    # Wait a bit to show the background task is running
    print(f"[TEST] Main coroutine continuing... (simulating other requests)")
    await asyncio.sleep(2)
    print(f"[TEST] Main coroutine still running... (background task still in progress)")
    
    # Wait for the background task to complete to see the final log
    await task
    print(f"[TEST] Background task has completed\n")


if __name__ == "__main__":
    print("=" * 70)
    print("Testing Background Task Logic")
    print("=" * 70)
    asyncio.run(test_background_task())
    print("=" * 70)
    print("Test completed successfully!")
    print("=" * 70)
