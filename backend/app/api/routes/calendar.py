from fastapi import APIRouter


from app.engines.macro.economic_calendar.engine import (
    build_economic_calendar,
)



router = APIRouter(
    prefix="/calendar",
    tags=["Calendar"]
)



@router.get("")
def calendar():


    return {

        "success": True,

        **build_economic_calendar()

    }