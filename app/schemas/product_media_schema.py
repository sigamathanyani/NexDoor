from pydantic import BaseModel

class RequestPresignedUrlData(BaseModel):
    product_id: int
    content_type: str
    
class S3MediaObjectResponse(BaseModel):
    presigned_url: str
    s3_key: str

class CreateProductMediaObject(BaseModel):
    s3_key: str