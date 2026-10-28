from urllib.parse import quote_plus
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Knowiix API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "knowiix_super_secret_jwt_key_development_2026_x89f!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    ALGORITHM: str = "HS256"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Firebase settings
    FIREBASE_CREDENTIALS_PATH: str = ""
    USE_MOCK_FIREBASE: bool = True
    
    # MySQL Database Settings
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DATABASE: str = "demo"
    USE_MYSQL: bool = True

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        encoded_user = quote_plus(self.MYSQL_USER) if self.MYSQL_USER else ""
        if self.MYSQL_PASSWORD:
            encoded_password = quote_plus(self.MYSQL_PASSWORD)
            return f"mysql+pymysql://{encoded_user}:{encoded_password}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        return f"mysql+pymysql://{encoded_user}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    # Code Execution Sandbox
    SANDBOX_TIMEOUT_SECONDS: int = 5
    SANDBOX_MAX_MEMORY_MB: int = 256

    # Gmail SMTP Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_NAME: str = "Knowiix Security"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
