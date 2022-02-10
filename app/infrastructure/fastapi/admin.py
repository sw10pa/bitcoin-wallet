from fastapi import APIRouter, Depends

from app.core.admin.admin_interactor import StatisticsRequest, StatisticsResponse
from app.core.facade import BTCWalletService
from app.infrastructure.fastapi.dependables import get_core

admin_api = APIRouter()


@admin_api.get("/statistics")
def get_statistics(
    api_key: str, core: BTCWalletService = Depends(get_core)
) -> StatisticsResponse:
    request = StatisticsRequest(api_key=api_key)
    return core.get_statistics(request)
