from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import user_router, auth_router

app = FastAPI(title="My home API")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router.router)
app.include_router(auth_router.router)
# app.include_router(listing_router.router)
# app.include_router(reservation_router.router)
