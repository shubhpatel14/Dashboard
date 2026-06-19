from fastapi import APIRouter
from app.services.risk_service import get_risk_analysis

router = APIRouter(
    prefix="/risk",
    tags=["Risk"]
)


@router.get("")
def get_risk():
    """
    Get the macroeconomic risk profile of Trishula Capital Terminal.
    """
    return get_risk_analysis()
