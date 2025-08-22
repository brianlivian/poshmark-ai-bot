from __future__ import annotations
from typing import Dict
from config import MAX_PRICE, SIZES

# Rough brand priors; tweak to taste
BRAND_BOOST = {
    "Ermenegildo Zegna": 0.25,
    "Canali": 0.25,
    "Isaia": 0.3,
    "Kiton": 0.35,
    "Gucci": 0.25,
    "Ralph Lauren Purple Label": 0.3,
    "SuitSupply": 0.15,
    "Hugo Boss": 0.1,
}

CONDITION_KEYWORDS = {
    "NWT": 0.2,
    "New with tags": 0.2,
    "Like new": 0.15,
    "Excellent": 0.1,
}


def _brand_from_title(title: str) -> str:
    for b in BRAND_BOOST:
        if b.lower() in title.lower():
            return b
    return ""


def compute_score(listing: Dict, vision: Dict) -> Dict:
    title = listing.get("title", "")
    price = vision.get("listed_price", 9999.0)

    # Price score (linear until cap)
    price_score = max(0.0, min(1.0, (MAX_PRICE - price) / MAX_PRICE))

    # Size match bonus if the title mentions one of the desired sizes
    size_bonus = 0.0
    for s in SIZES:
        if s.lower() in title.lower():
            size_bonus = 0.1
            break

    # Brand boost
    brand = _brand_from_title(title)
    brand_bonus = BRAND_BOOST.get(brand, 0.0)

    # Condition hints from title
    cond_bonus = 0.0
    for k, v in CONDITION_KEYWORDS.items():
        if k.lower() in title.lower():
            cond_bonus = max(cond_bonus, v)

    # Vision components
    modern = 0.2 if vision.get("is_modern") else 0.0
    style = 0.3 * float(vision.get("style_score", 0.0))
    condition = 0.2 * float(vision.get("condition_score", 0.0))
    price_ok = 0.1 if vision.get("price_ok") else 0.0

    total = price_score + size_bonus + brand_bonus + cond_bonus + modern + style + condition + price_ok
    total = max(0.0, min(1.0, total))

    return {
        "score": total,
        "brand_detected": brand,
        "explanations": {
            "price_score": price_score,
            "size_bonus": size_bonus,
            "brand_bonus": brand_bonus,
            "cond_bonus": cond_bonus,
            "modern": modern,
            "style_component": style,
            "condition_component": condition,
            "price_ok_component": price_ok,
        },
    }


