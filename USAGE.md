# Usage Guide

## How It Works

This demo shows how to use FastAPI's `BackgroundTasks` feature with SkyWalking tracing.

### The /test Endpoint

When you call the `/test` endpoint:

1. **Request arrives**: FastAPI receives the HTTP GET request
2. **Background task created**: A coroutine is scheduled to run in the background
3. **Immediate response**: The endpoint returns `"ok"` without waiting for the task
4. **Background execution**: The task runs for 10 seconds in the background
5. **Task completion**: The task finishes after the response has already been sent

### Key Features

#### Non-blocking Response
```python
@app.get("/test")
async def test_endpoint(background_tasks: BackgroundTasks):
    task_id = f"task-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}"
    
    # Schedule background task
    background_tasks.add_task(background_sleep_task, task_id)
    
    # Return immediately - don't wait for task
    return "ok"
```

#### Background Task Implementation
```python
async def background_sleep_task(task_id: str):
    start_time = datetime.now()
    logger.info(f"[{task_id}] Background task started at {start_time}")
    
    # This sleep happens AFTER the response is sent
    await asyncio.sleep(10)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"[{task_id}] Background task completed at {end_time} (duration: {duration}s)")
```

## Example Scenarios

### Scenario 1: Single Request

```bash
# Terminal 1: Start the server
python main.py

# Terminal 2: Make a request
time curl http://localhost:8000/test
```

**Expected Result:**
- Response returns in < 1 second with "ok"
- Server logs show task starts immediately
- Server logs show task completes after ~10 seconds

**Server Logs:**
```
INFO:__main__:[task-20240101-120000-123456] Endpoint returning immediately
INFO:     127.0.0.1:xxxxx - "GET /test HTTP/1.1" 200 OK
INFO:__main__:[task-20240101-120000-123456] Background task started at 2024-01-01 12:00:00.123456
INFO:__main__:[task-20240101-120000-123456] Background task completed at 2024-01-01 12:00:10.123456 (duration: 10.0s)
```

### Scenario 2: Multiple Concurrent Requests

```bash
# Make 3 requests quickly
curl http://localhost:8000/test &
curl http://localhost:8000/test &
curl http://localhost:8000/test &
```

**Expected Result:**
- All 3 requests return immediately (within 1 second)
- 3 background tasks run concurrently
- All tasks complete after ~10 seconds (not 30 seconds!)

### Scenario 3: With SkyWalking Tracing

When running with SkyWalking enabled, you can:

1. Start the full stack:
   ```bash
   docker-compose up
   ```

2. Make requests:
   ```bash
   curl http://localhost:8000/test
   ```

3. View traces in SkyWalking UI:
   - Open http://localhost:8080
   - Navigate to "Topology" to see service map
   - Navigate to "Trace" to see individual requests
   - You'll see the main request trace
   - Background task execution is traced separately

## Common Use Cases

This pattern is useful for:

1. **Email/Notification sending**: Return success to user, send email in background
2. **Data processing**: Accept upload, process file in background
3. **Logging/Analytics**: Record event in background without blocking response
4. **Cache warming**: Trigger cache update without waiting
5. **Webhook delivery**: Send webhook, return to caller immediately

## Code Architecture

```
main.py
├── FastAPI app initialization
├── /test endpoint
│   ├── Creates unique task ID
│   ├── Schedules background_sleep_task
│   └── Returns "ok" immediately
├── background_sleep_task coroutine
│   ├── Logs start time
│   ├── Sleeps for 10 seconds
│   └── Logs completion time
└── / root endpoint (health check)
```

## Performance Characteristics

- **Response Time**: < 100ms (typically < 10ms)
- **Background Task Duration**: Exactly 10 seconds
- **Concurrency**: Multiple background tasks run in parallel
- **Resource Usage**: Each background task uses minimal memory
- **Server Capacity**: Can handle thousands of background tasks

## Testing the Logic

Run the test script to see the behavior without a web server:

```bash
python test_app.py
```

This demonstrates:
- Creating an async task
- Returning immediately
- Task continuing in background
- Task completion after 10 seconds

## Troubleshooting

### Background task doesn't run
- Make sure you're using `BackgroundTasks` from FastAPI
- Ensure the server stays running until tasks complete
- Check server logs for errors

### Task runs but response is slow
- Verify you're using `background_tasks.add_task()` not `await`
- Check there's no blocking code before the return statement

### SkyWalking not tracing
- Verify OAP server is running and accessible
- Check environment variables are set correctly
- Look for SkyWalking agent startup logs
- Ensure `sw-python` command is used to start the app
