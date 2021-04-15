from fastapi import APIRouter

from candlebot.api.strategies import ema

router = APIRouter(
    prefix="/strategies",
    tags=["strategies"],
    responses={404: {"description": "Not found"}},
)


@router.get("/ema")
async def strategy_ema():
    return ema.calc()
