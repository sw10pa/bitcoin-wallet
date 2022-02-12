from dataclasses import dataclass
from typing import Optional, Protocol

from app.core.admin.admin_repository import IAdminRepository
from app.core.entities import StatisticsInfo
from app.core.utils import Response


@dataclass
class StatisticsRequest:
    api_key: str


@dataclass
class StatisticsResponse(Response):
    statistics_info: Optional[StatisticsInfo]


class IAdminInteractor(Protocol):
    def get_statistics(self, request: StatisticsRequest) -> StatisticsResponse:
        pass


class AdminInteractor:
    __admin_key = "Stephane27"

    def __init__(self, admin_repository: IAdminRepository):
        self.admin_repository = admin_repository

    def get_statistics(self, request: StatisticsRequest) -> StatisticsResponse:
        if request.api_key != self.__admin_key:
            return StatisticsResponse(
                success=False,
                message="Invalid API key",
                statistics_info=None,
            )

        all_transactions = self.admin_repository.fetch_all_transactions()
        transaction_count = len(all_transactions)
        profit = sum([t.btc_amount * t.fee_pct for t in all_transactions])
        return StatisticsResponse(
            success=True,
            message="OK",
            statistics_info=StatisticsInfo(transaction_count, profit),
        )
