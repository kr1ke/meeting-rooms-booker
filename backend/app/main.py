from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, rooms, bookings, users, departments, notifications, settings

app = FastAPI(title="Booking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(bookings.router)
app.include_router(users.router)
app.include_router(departments.router)
app.include_router(notifications.router)
app.include_router(settings.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
