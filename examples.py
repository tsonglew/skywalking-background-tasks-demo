"""
Extended examples showing real-world use cases for background tasks.
These examples demonstrate practical applications beyond the simple sleep demo.
"""
import asyncio
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Background Tasks Real-World Examples")


# Example 1: Email notification simulation
async def send_email_notification(user_email: str, message: str):
    """Simulate sending an email notification in the background."""
    logger.info(f"Starting email send to {user_email}")
    await asyncio.sleep(2)  # Simulate email API call
    logger.info(f"Email sent to {user_email}: {message}")


@app.post("/register")
async def register_user(email: str, background_tasks: BackgroundTasks):
    """
    User registration endpoint that sends welcome email in background.
    Returns immediately after registration, email sent asynchronously.
    """
    # Register user (fast operation)
    user_id = f"user-{datetime.now().timestamp()}"
    
    # Schedule email to be sent in background
    background_tasks.add_task(
        send_email_notification,
        email,
        "Welcome to our service!"
    )
    
    return {
        "user_id": user_id,
        "email": email,
        "status": "registered",
        "note": "Welcome email will be sent shortly"
    }


# Example 2: Data processing simulation
async def process_uploaded_file(file_id: str, file_size: int):
    """Simulate processing an uploaded file."""
    logger.info(f"Starting processing for file {file_id} ({file_size} bytes)")
    
    # Simulate various processing steps
    await asyncio.sleep(1)  # Extract metadata
    logger.info(f"[{file_id}] Metadata extracted")
    
    await asyncio.sleep(2)  # Generate thumbnails
    logger.info(f"[{file_id}] Thumbnails generated")
    
    await asyncio.sleep(1)  # Update database
    logger.info(f"[{file_id}] Database updated")
    
    logger.info(f"[{file_id}] Processing complete")


@app.post("/upload")
async def upload_file(filename: str, size: int, background_tasks: BackgroundTasks):
    """
    File upload endpoint that processes file in background.
    Returns upload confirmation immediately, processing happens asynchronously.
    """
    file_id = f"file-{datetime.now().timestamp()}"
    
    # Schedule background processing
    background_tasks.add_task(process_uploaded_file, file_id, size)
    
    return {
        "file_id": file_id,
        "filename": filename,
        "size": size,
        "status": "uploaded",
        "note": "File is being processed in the background"
    }


# Example 3: Analytics logging
async def log_analytics_event(event_type: str, user_id: str, data: dict):
    """Log analytics event to external service."""
    logger.info(f"Logging analytics: {event_type} for user {user_id}")
    await asyncio.sleep(0.5)  # Simulate API call to analytics service
    logger.info(f"Analytics logged: {event_type}")


@app.get("/product/{product_id}")
async def view_product(product_id: str, user_id: str, background_tasks: BackgroundTasks):
    """
    Product view endpoint that logs analytics in background.
    Returns product data immediately, analytics logged asynchronously.
    """
    # Schedule analytics logging
    background_tasks.add_task(
        log_analytics_event,
        "product_view",
        user_id,
        {"product_id": product_id, "timestamp": datetime.now().isoformat()}
    )
    
    # Return product data immediately
    return {
        "product_id": product_id,
        "name": f"Product {product_id}",
        "price": 99.99,
        "in_stock": True
    }


# Example 4: Cache warming
async def warm_cache(cache_key: str, expensive_operation: str):
    """Simulate warming a cache with expensive computation."""
    logger.info(f"Starting cache warm for {cache_key}")
    await asyncio.sleep(3)  # Simulate expensive computation
    logger.info(f"Cache warmed for {cache_key}: {expensive_operation}")


@app.post("/invalidate-cache")
async def invalidate_cache(cache_key: str, background_tasks: BackgroundTasks):
    """
    Cache invalidation endpoint that warms cache in background.
    Returns immediately, cache rebuilt asynchronously.
    """
    # Schedule cache warming
    background_tasks.add_task(
        warm_cache,
        cache_key,
        "expensive_computation_result"
    )
    
    return {
        "cache_key": cache_key,
        "status": "invalidated",
        "note": "Cache is being warmed in the background"
    }


# Example 5: Multiple background tasks
@app.post("/complete-order")
async def complete_order(
    order_id: str,
    user_email: str,
    background_tasks: BackgroundTasks
):
    """
    Order completion that triggers multiple background tasks.
    Demonstrates running multiple tasks for a single endpoint.
    """
    # Schedule multiple background tasks
    background_tasks.add_task(
        send_email_notification,
        user_email,
        f"Order {order_id} confirmed!"
    )
    
    background_tasks.add_task(
        log_analytics_event,
        "order_completed",
        user_email,
        {"order_id": order_id}
    )
    
    background_tasks.add_task(
        warm_cache,
        f"user-orders-{user_email}",
        "fetch_user_order_history"
    )
    
    return {
        "order_id": order_id,
        "status": "completed",
        "note": "Email, analytics, and cache updates scheduled"
    }


@app.get("/")
def root():
    """List all available example endpoints."""
    return {
        "message": "Background Tasks Real-World Examples",
        "endpoints": {
            "POST /register": "User registration with email notification",
            "POST /upload": "File upload with background processing",
            "GET /product/{product_id}": "Product view with analytics logging",
            "POST /invalidate-cache": "Cache invalidation with warming",
            "POST /complete-order": "Order completion with multiple tasks"
        },
        "note": "All endpoints return immediately while tasks run in background"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
