from enum import Enum


class SortBy(Enum):
    PRICE = "PRICE"
    RATING = "RATING"
    
class SortOrder(Enum):
    ASC = 'ASC'
    DESC = 'DESC'