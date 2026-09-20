from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    SECRET_KEY: str
    ALGORITHM: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_BUCKET_NAME: str
    AWS_REGION: str
    PAYSTACK_SECRET_KEY: str
    PAYSTACK_TEST_PUBLIC_KEY: str
    PAYSTACK_URL: str
    NGROK_AUTHTOKEN: str
    RESEND_EMAIL_API_KEY: str
    
    model_config = SettingsConfigDict(env_file='.env.example', env_file_encoding='utf-8')
    
settings = Settings()
