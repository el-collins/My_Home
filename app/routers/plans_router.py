from fastapi import APIRouter, Depends, HTTPException, Path
from app.models import PlanName, PricingPlan, pricing_plans_db
from typing import Dict


router = APIRouter(prefix="/plans", tags=["pricing-plans"])

# Endpoint to get pricing plans


@router.get("/", response_model=Dict[PlanName, PricingPlan])
async def get_pricing_plans():
    return pricing_plans_db

# Endpoint to get pricing plan by name


@router.get("/{plan_name}", response_model=PricingPlan)
async def get_pricing_plan_by_name(plan_name: PlanName = Path(..., title="Plan Name")):
    price = pricing_plans_db.get(plan_name)
    if price is None:
        raise HTTPException(status_code=404, detail="Plan not found")

    return PricingPlan(name=plan_name, price=price)

# Endpoint to update pricing plan


@router.post("/{plan_name}")
async def update_pricing_plan(plan_name: PlanName = Path(..., title="Plan Name"), new_price: float = Path(..., title="New Price")):
    if plan_name not in pricing_plans_db:
        raise HTTPException(status_code=400, detail="Invalid plan name")

    pricing_plans_db[plan_name] = new_price
    return {"message": f"Pricing plan {plan_name} updated with new price {new_price}"}
