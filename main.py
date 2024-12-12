from fastapi import FastAPI
from routes import posts, users

from core.database import initialize_db, get_client

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Include your routers
app.include_router(posts.router, prefix="/posts", tags=["Posts"])
app.include_router(users.router, prefix="/users", tags=["Users"])

@app.on_event("startup")
async def startup_event():
    initialize_db()

@app.on_event("shutdown")
async def shutdown_event():
    client = get_client()
    if client:
        client.close()
