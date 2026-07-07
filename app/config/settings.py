import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY"
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

    # Evolution API
    EVOLUTION_URL = os.getenv("EVOLUTION_URL")
    EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE")
    EVOLUTION_TOKEN = os.getenv("EVOLUTION_TOKEN")

    WHATSAPP_ADMIN = os.getenv("WHATSAPP_ADMIN")