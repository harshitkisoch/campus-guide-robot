import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve the root directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """
    Validates and stores application configurations loaded from the environment/.env.
    Type constraints are checked at startup to prevent invalid values.
    """
    # Gemini API settings
    gemini_api_key: str = Field(..., alias="GEMINI_API_KEY")
    gemini_model: str = Field("gemini-3.5-flash-lite", alias="GEMINI_MODEL")

    # Text-To-Speech settings
    tts_rate: int = Field(160, alias="TTS_RATE")
    tts_volume: float = Field(1.0, alias="TTS_VOLUME")

    # USB Serial configuration
    serial_port: str = Field(..., alias="SERIAL_PORT")
    serial_baud_rate: int = Field(115200, alias="SERIAL_BAUD_RATE")

    # WebSocket communication (Phase 4)
    ws_host: str = Field("0.0.0.0", alias="WS_HOST")
    ws_port: int = Field(8765, alias="WS_PORT")

    # Tell Pydantic settings where to find the local .env file
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore" # Ignore extra env variables not declared here
    )

# Instantiate the global settings container.
# If config is invalid, Pydantic raises an error immediately at startup.
try:
    settings = Settings()
except Exception as e:
    print("\n[CRITICAL CONFIG ERROR] Failed to load or validate configurations.")
    print("Please check that your '.env' file exists in the root and variables match their type requirements.")
    print(f"Details: {e}\n")
    raise e
