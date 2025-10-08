# Architecture Overview

## Request Flow Diagram

```
Client Request → FastAPI Server → Background Task Queue
      ↓              ↓                    ↓
   "GET /test"    Schedule Task       Task Runs
      ↓              ↓                    ↓
   Response       Return "ok"      Sleep 10s
   ← "ok" ←      Immediately          ↓
   (< 100ms)                      Complete
                                  (after 10s)
```

## Detailed Flow

### 1. Request Arrival
```
Time: T+0ms
─────────────────────────────────────────
Client sends GET /test
→ FastAPI receives request
→ Creates unique task_id
```

### 2. Background Task Scheduling
```
Time: T+1ms
─────────────────────────────────────────
→ background_tasks.add_task() called
→ Task scheduled in internal queue
→ Task does NOT execute yet
```

### 3. Immediate Response
```
Time: T+2ms
─────────────────────────────────────────
→ Endpoint returns "ok"
→ HTTP response sent to client
→ Client receives response
   ✓ Request complete from client perspective
```

### 4. Background Execution
```
Time: T+3ms → T+10003ms
─────────────────────────────────────────
→ Background task starts executing
→ Logs: "Background task started"
→ await asyncio.sleep(10)
   ... 10 seconds pass ...
→ Logs: "Background task completed"
   ✓ Background task complete
```

## Timeline Comparison

### Without Background Tasks (Blocking)
```
Client Request ────────────────────────────────> Response
               [Wait 10 seconds]                 (10+ seconds)
               User must wait!
```

### With Background Tasks (Non-blocking)
```
Client Request ──> Response
               ↓   (< 100ms)
               ↓   User continues!
               ↓
               └──> Background Task
                    [Executes separately]
                    (10 seconds, invisible to user)
```

## Component Architecture

```
┌─────────────────────────────────────────────────────┐
│                  FastAPI Application                 │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────────┐         ┌───────────────────┐    │
│  │   /test      │         │ Background Task   │    │
│  │  Endpoint    │────────▶│     Queue         │    │
│  └──────────────┘         └───────────────────┘    │
│        │                           │                 │
│        │                           │                 │
│        ▼                           ▼                 │
│  Return "ok"              background_sleep_task()   │
│  immediately              runs asynchronously       │
│                                                       │
└─────────────────────────────────────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  SkyWalking Agent     │
        │  (Tracing)            │
        └───────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  SkyWalking OAP       │
        │  (Collector)          │
        └───────────────────────┘
```

## Concurrency Model

### Single Request
```
Main Thread:
├─ Receive request (T+0)
├─ Schedule task (T+1)
├─ Return response (T+2)
└─ Done

Background Task:
    ├─ Start (T+3)
    ├─ Sleep (T+3 to T+10003)
    └─ Complete (T+10003)
```

### Multiple Concurrent Requests
```
Request 1:
├─ Main: Return "ok" (T+0 to T+2)
└─ Background: Run (T+3 to T+10003)

Request 2:
├─ Main: Return "ok" (T+5 to T+7)
└─ Background: Run (T+8 to T+10008)

Request 3:
├─ Main: Return "ok" (T+10 to T+12)
└─ Background: Run (T+13 to T+10013)

All background tasks run in parallel!
```

## SkyWalking Integration

### Trace Hierarchy
```
Span: HTTP GET /test
├─ Span: FastAPI request handling
│  ├─ Duration: ~2ms
│  └─ Status: 200 OK
│
└─ Span: background_sleep_task
   ├─ Duration: ~10000ms
   ├─ Parent: Same trace context
   └─ Runs after response sent
```

### Trace Timeline
```
0ms    ├─ HTTP Request arrives
1ms    ├─ Endpoint logic executes
2ms    ├─ Response sent ──────────┐
3ms    ├─ Background task starts  │
       │                           │ (User already has response)
       │                           │
10003ms└─ Background task ends    │
                                   │
                                   ▼
                              User happy! 😊
```

## Key Benefits

1. **User Experience**
   - Instant response (< 100ms)
   - No waiting for background operations
   - Perceived performance improvement

2. **Resource Efficiency**
   - Server handles more requests
   - Background tasks run in parallel
   - No thread blocking

3. **Observability**
   - Full SkyWalking tracing
   - Background tasks tracked
   - Performance metrics available

4. **Scalability**
   - Handle thousands of background tasks
   - Non-blocking architecture
   - Efficient resource usage

## Common Patterns

### Pattern 1: Fire and Forget
```python
@app.post("/action")
async def action(background_tasks: BackgroundTasks):
    background_tasks.add_task(long_running_task)
    return {"status": "processing"}
```

### Pattern 2: Multiple Background Tasks
```python
@app.post("/complex-action")
async def complex_action(background_tasks: BackgroundTasks):
    background_tasks.add_task(task1)
    background_tasks.add_task(task2)
    background_tasks.add_task(task3)
    return {"status": "processing", "tasks": 3}
```

### Pattern 3: Background Task with Parameters
```python
@app.post("/process")
async def process(data: dict, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_data, data)
    return {"status": "accepted", "id": data["id"]}
```

## Error Handling

### Background Task Errors
```
If background task fails:
├─ User already received success response
├─ Error logged in application logs
├─ SkyWalking captures error trace
└─ Consider:
   ├─ Dead letter queue
   ├─ Retry mechanism
   └─ Error notification system
```

### Best Practices
1. Background tasks should be idempotent
2. Log all errors with task context
3. Use SkyWalking to track failures
4. Consider implementing retry logic
5. Don't rely on background tasks for critical operations

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Response Time | < 100ms |
| Background Task Duration | 10,000ms |
| Time Saved per Request | 9,900ms |
| Concurrent Capacity | 1000+ tasks |
| Memory per Task | < 1MB |
| CPU Usage | Minimal (mostly sleeping) |

## Comparison with Alternatives

### Background Tasks vs Celery
- **Background Tasks**: Simple, built-in, good for light tasks
- **Celery**: Separate process, persistent queue, good for heavy/critical tasks

### Background Tasks vs Threading
- **Background Tasks**: Async, non-blocking, efficient
- **Threading**: Synchronous, can block, higher overhead

### Background Tasks vs Message Queue
- **Background Tasks**: In-process, no external dependencies
- **Message Queue**: Distributed, persistent, more reliable
