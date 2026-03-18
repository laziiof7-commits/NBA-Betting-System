# --------------------------------------------------
# 💰 DASHBOARD (ROI + STATS)
# --------------------------------------------------

from fastapi import APIRouter
from prop_tracker import summary
from clv_tracker import calculate_clv

router = APIRouter()

@router.get("/dashboard")
def dashboard():

    return {
        "performance": summary(),
        "clv": calculate_clv()
    }