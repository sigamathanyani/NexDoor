from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    SECRET_KEY: str
    ALGORITHM: str
    
    model_config = SettingsConfigDict(env_file='.env.example', env_file_encoding='utf-8')
    
settings = Settings()