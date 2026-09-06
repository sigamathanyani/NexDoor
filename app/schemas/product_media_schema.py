from pydantic import BaseModel


class RequestPresignedUrlData(BaseModel):
    content_type: str


class S3MediaObjectResponse(BaseModel):
    presigned_url: str | list[str]
    s3_key: str


class CreateProductMediaObject(BaseModel):
    s3_key: str
    name: str
    is_primary: bool


class ProductMediaResponse(BaseModel):
    name: str
