from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.router import authRoute


# Define app lifespan — this runs once when the app starts and when it shuts down
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield  # 👈 After this, FastAPI starts handling requests
    # Optionally: add cleanup tasks here (closing connections, etc.)


# Initialize the FastAPI app with the custom lifespan
app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Hello, FastAPI with uv!"}


app.include_router(authRoute.router)
