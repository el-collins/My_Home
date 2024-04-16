from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import user_router, auth_router, property_router, wishlist_router

app = FastAPI(title="My home API")

origins = ["http://localhost:5173"]
# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router.router)
app.include_router(auth_router.router)
app.include_router(property_router.router)
app.include_router(wishlist_router.router)
# app.include_router(google_router.router)
