from pydantic import BaseModel


class StatsByStatus(BaseModel):
    """Promise counts broken down by resolved_status.

    Plain BaseModel — constructed explicitly from GROUP BY aggregate results.
    """

    kept: int
    broken: int
    in_progress: int
    stalled: int
    not_rated: int


class StatsOut(BaseModel):
    """Homepage stats response — total approved promises + breakdown by resolved_status.

    Plain BaseModel — no ORM object; constructed explicitly from aggregate query.
    """

    total: int
    by_status: StatsByStatus
