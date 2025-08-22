from __future__ import annotations
import json
from typing import Dict
from openai import OpenAI
from config import OPENAI_API_KEY, VISION_MODEL, MAX_PRICE

client = OpenAI(api_key=OPENAI_API_KEY)

SCHEMA = {
    "type": "object",
    "properties": {
        "is_modern": {"type": "boolean"},
        "style_score": {"type": "number"},
        "condition_score": {"type": "number"},
        "fit_guess": {"type": "string"},
        "price_ok": {"type": "boolean"},
        "reason": {"type": "string"}
    },
    "required": ["is_modern", "style_score", "condition_score", "price_ok", "reason"]
}

PROMPT = (
    "You are a fashion evaluator. Judge if the pictured men's suit looks modern, stylish, and in good condition "
    "for a young professional. Consider current fit (not boxy), lapel width, silhouette, and overall vibe. "
    f"Treat under ${int(MAX_PRICE)} as a good price if the suit appears designer or excellent. "
    "Return STRICT JSON matching the provided schema."
)


def evaluate_listing(image_url: str, title: str, price_str: str, brand_hint: str = "") -> Dict:
    # normalize price
    try:
        p = float(price_str.replace("$", "").replace(",", "").strip())
    except Exception:
        p = 9999.0

    messages = [
        {"role": "system", "content": PROMPT},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": json.dumps({
                    "title": title,
                    "brand_hint": brand_hint,
                    "listed_price": p
                })},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        },
    ]

    # Ask model to return JSON; if it returns text, we try to parse best-effort
    resp = client.chat.completions.create(
        model=VISION_MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=300,
    )
    txt = resp.choices[0].message.content or "{}"
    try:
        data = json.loads(txt)
    except Exception:
        # crude fallback: find first JSON object in text
        start = txt.find("{")
        end = txt.rfind("}")
        data = json.loads(txt[start:end+1]) if start >= 0 and end > start else {}

    # light defaults
    data.setdefault("is_modern", False)
    data.setdefault("style_score", 0.0)
    data.setdefault("condition_score", 0.0)
    data.setdefault("price_ok", False)
    data.setdefault("fit_guess", "unknown")

    return {**data, "listed_price": p}