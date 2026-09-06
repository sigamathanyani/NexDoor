import uuid

from app.config import settings

from botocore.exceptions import ClientError

from app.exceptions.app_exception import AppException
from app.utils.error_codes import ErrorCode

from fastapi import status


def get_presigned_url_helper(s3_key: str, client_method, s3_client, content_type):
    method_params = {
        "Bucket": settings.AWS_S3_BUCKET_NAME,
        "Key": s3_key,  # will be different for get - we have it in the DB
    }
    if client_method == "put_object":
        method_params["ContentType"] = content_type

    expires_in = 3600

    try:
        presigned_url = s3_client.generate_presigned_url(
            ClientMethod=client_method, Params=method_params, ExpiresIn=expires_in
        )
    except ClientError as e:
        error_helper(e)

    return presigned_url


def get_s3_key():
    extension = "png"  # data.content_type.split("/")[1]
    file_id = str(uuid.uuid4())
    file_unique_name = f"products/{file_id}.{extension}"  # S3 keys
    return file_unique_name


def error_helper(e):
    code = e.response["Error"]["Code"]
    if code == "NoSuchKey":
        raise AppException(
            message="Media does not exist",
            error_code=ErrorCode.MEDIA_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    elif code == "403":
        raise AppException(
            message="You do not have permissions to perform this action",
            error_code=ErrorCode.S3_UNAUTHORIZED,
            status_code=status.HTTP_403_FORBIDDEN,
        )

    else:
        raise AppException(
            message="An error occured while accessing media storage",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
