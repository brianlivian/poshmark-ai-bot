from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_GOAL = (
    "Find modern suits under $150 in sizes 42–44R and alert me."
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("openai_api")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

MAX_PRICE = float(os.getenv("MAX_PRICE", 150))
SIZES = [s.strip() for s in os.getenv("SIZES", "42R,43R,44R").split(",") if s.strip()]
BRANDS = [b.strip() for b in os.getenv("BRANDS", "").split(",") if b.strip()]

HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
SCRAPE_MAX_ITEMS = int(os.getenv("SCRAPE_MAX_ITEMS", 60))

SQLITE_PATH = os.path.join(os.getcwd(), "data.db")
VISION_MODEL = "gpt-4o-2024-08-06"

REQUESTS_PER_MINUTE = 40
SLEEP_BETWEEN_LISTINGS = 0.6
