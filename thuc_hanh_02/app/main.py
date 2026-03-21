from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import search
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
import os

# Prefix API theo version
api_prefix = f"/api/{settings.VERSION_APP}"

# Tạo instance của FastAPI
app = FastAPI(
    title=settings.TITLE_APP,
    docs_url=f"{api_prefix}/docs",
    redoc_url=f"{api_prefix}/redoc",
    openapi_url=f"{api_prefix}/openapi.json",
)

# Serve static dataset
if os.path.exists(settings.DATASET_DIR):
    app.mount("/dataset", StaticFiles(directory=settings.DATASET_DIR), name="dataset")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include các router vào ứng dụng chính
app.include_router(search.router, prefix=api_prefix)

@app.get(f"{api_prefix}/")
def read_root():
    return {"message": f"Welcome to {settings.TITLE_APP}"}
