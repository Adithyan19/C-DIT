import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


class Settings(BaseSettings):
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    DATABASE_URL: str = ""
    SECRET_KEY: str = "farmer-chatbot-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    SUPABASE_STORAGE_URL: str = ""
    SUPABASE_IMAGE_BUCKET: str = "disease-images"
    SUPABASE_VOICE_BUCKET: str = "voice-messages"

    # Superuser credentials
    SUPERUSER_EMAIL: str = "admin@farmbot.com"
    SUPERUSER_PASSWORD: str = "SuperAdmin123!"
    SUPERUSER_NAME: str = "Admin"

    model_config = {"env_file": ".env", "extra": "allow"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DATABASE_URL:
            self.DATABASE_URL = self.SUPABASE_URL
        # Build Supabase storage URL from project ref
        if not self.SUPABASE_STORAGE_URL and self.SUPABASE_KEY:
            # Extract project ref from the JWT or use known ref
            self.SUPABASE_STORAGE_URL = (
                "https://armsvahocpfwzqdatuuo.supabase.co/storage/v1"
            )


settings = Settings()
