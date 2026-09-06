from enum import Enum


class PricingUnit(Enum):
    HOUR: str = "HOUR"
    DAY: str = "DAY"
    WEEK: str = "WEEK"
    SERVICE: str = "SERVICE"
    ONE_TIME: str = "ONE_TIME"
