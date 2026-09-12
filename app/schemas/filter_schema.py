from pydantic import BaseModel

class FilterParams(BaseModel):
    model_config = {"extra": "allow"}
    
    product_query: str | None = None # query_params
    product_filter: str | None = None # query_params
    # product_description_query: str | None = None # query_params
    # order_by: Literal["createdAt", "updatedAt"] = "createdAt"