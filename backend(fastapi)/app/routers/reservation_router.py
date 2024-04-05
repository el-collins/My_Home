from fastapi import APIRouter, Depends
from app import crud, dependencies
from app.models import ReservationCreate, ReservationPublic

router = APIRouter(prefix="/reservations", tags=["reservations"])

@router.post("/", response_model=ReservationPublic)
async def create_reservation(reservation: ReservationCreate, db=Depends(dependencies.get_db)):
    return await crud.create_reservation(db, reservation)

@router.get("/{reservation_id}", response_model=ReservationPublic)
async def get_reservation(reservation_id: str, db=Depends(dependencies.get_db)):
    return await crud.get_reservation(db, reservation_id)

# Additional reservation-related endpoints would go here...