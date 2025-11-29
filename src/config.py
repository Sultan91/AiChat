from pydantic import PostgresDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = "openai/gpt-oss-20b:free"
KB_PATH = "knowledge_base"

