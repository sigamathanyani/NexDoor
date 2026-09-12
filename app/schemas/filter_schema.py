from pydantic import BaseModel

from app.enums.categories import Category
from app.enums.product_type import ProductType
from app.enums.sorting import SortBy, SortOrder

class FilterParams(BaseModel):
    model_config = {"extra": "allow"}
    
    product_query: str | None = None # query_params
    product_type: list[ProductType] | None = None # query_params
    category_filter: list[Category] | None = None # query_params
    sort_by: SortBy | None = None
    sort_order: SortOrder | None = None
