from enum import Enum


class ContentType(Enum):
    JPEG: str = "image/jpeg"
    PNG: str = "image/png"
    WEBP: str = "image/webp"
    MP4: str = "video/mp4"
