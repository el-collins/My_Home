from fastapi import APIRouter, Depends, HTTPException, Path
from app.models import PlanName, PricingPlan, pricing_plans_db
from typing import Dict


router = APIRouter(prefix="/api/v1/plans", tags=["pricing-plans"])


# Endpoint to get pricing plans
@router.get("/", response_model=Dict[str, PricingPlan])
async def get_pricing_plans():
    return {plan_name.value: PricingPlan(name=plan_name, price=price) for plan_name, price in pricing_plans_db.items()}


# Endpoint to get pricing plan by name
@router.get("/{plan_name}", response_model=PricingPlan)
async def get_pricing_plan_by_name(plan_name: PlanName = Path(..., title="Plan Name")):
    price = pricing_plans_db.get(plan_name)
    if price is None:
        raise HTTPException(status_code=404, detail="Plan not found")

    return PricingPlan(name=plan_name, price=price)
