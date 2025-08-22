from __future__ import annotations
import json
import requests
from typing import List, Dict
from config import SLACK_WEBHOOK_URL


def _format_block(item: Dict) -> Dict:
    title = item["title"]
    price = item.get("price_str", "")
    url = item["url"]
    score = item.get("score", 0)
    brand = item.get("brand_detected", "")
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*{title}*\nScore: *{score:.2f}*  {price}  {brand}\n<{url}|Open listing>"
        },
        "accessory": {
            "type": "image",
            "image_url": item.get("image_url", ""),
            "alt_text": "suit"
        }
    }


def send_slack(found: List[Dict]):
    if not SLACK_WEBHOOK_URL:
        return
    if not found:
        return
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": "🎯 New good finds"}},
        {"type": "divider"}
    ]
    blocks.extend(_format_block(x) for x in found[:10])
    payload = {"blocks": blocks}
    try:
        requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=10)
    except Exception:
        pass