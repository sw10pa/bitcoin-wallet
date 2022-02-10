from dataclasses import dataclass
from typing import Protocol

from app.core.facade import Response
from app.core.repositories import IFatherRepository, StatisticsInfo


@dataclass
class StatisticsRequest:
    api_key: str


@dataclass
class StatisticsResponse(Response):
    statistics_info: StatisticsInfo


class IAdminInteractor(Protocol):
    def get_statistics(self, request: StatisticsRequest) -> StatisticsResponse:
        pass


class AdminInteractor:
    def __init__(
        self, transaction_repository: IFatherRepository
    ):  # TODO change to ITransactionRepository
        self.transactions_repository = transaction_repository

    def get_statistics(self, request: StatisticsRequest) -> StatisticsResponse:
        # TODO CHECK IF API KEY IS ADMIN
        all_transactions = self.transactions_repository.fetch_all_transactions()
        # TODO calculate statistics
        return StatisticsResponse(
            success=True, message="Temporary", statistics_info=StatisticsInfo(7, 5)
        )
        # if statistics_info is None:
        #     return StatisticsResponse(
        #         success=False,
        #         message="Statistics not found",
        #         statistics_info=statistics_info,
        #     )
        # return StatisticsResponse(
        #     success=True,
        #     message="Statistics found",
        #     statistics_info=statistics_info,
        # )
