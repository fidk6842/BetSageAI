import os
from dotenv import load_dotenv
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Load environment variables from .env file
load_dotenv(PROJECT_ROOT / '.env')

# Bot settings
BOT_TOKEN = os.getenv("BOT_TOKEN")
SCRAPING_API_KEY = os.getenv("SCRAPING_API_KEY")
SCRAPING_BASE_URL = os.getenv("SCRAPING_BASE_URL", "https://api.the-odds-api.com/v4")

# Validate required environment variables
required_vars = {
    "BOT_TOKEN": BOT_TOKEN,
    "SCRAPING_API_KEY": SCRAPING_API_KEY,
    "SCRAPING_BASE_URL": SCRAPING_BASE_URL
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")