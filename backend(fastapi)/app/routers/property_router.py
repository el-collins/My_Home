from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.database import create_property, get_property, update_property, delete_property
from app.models import Property, PropertyCreate, PropertyUpdate

router = APIRouter(tags=["properties"])


@router.post("/properties/")
async def create_property(property_data: PropertyCreate):
    return {"property_details": property_data}


@router.get("/properties/{property_id}")
async def read_property(property_id: str):
    property_data = await get_property(property_id)
    if property_data:
        return property_data
    raise HTTPException(status_code=404, detail="Property not found")


@router.put("/properties/{property_id}")
async def update_property_data(property_id: str, updated_data: PropertyUpdate):
    property_data = await update_property(property_id, updated_data.dict())
    if property_data:
        return property_data
    raise HTTPException(status_code=404, detail="Property not found")


@router.delete("/properties/{property_id}")
async def delete_property_data(property_id: str):
    result = await delete_property(property_id)
    if result:
        return JSONResponse(status_code=200, content=result)
    raise HTTPException(status_code=404, detail="Property not found")
