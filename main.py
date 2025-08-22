from __future__ import annotations
import argparse
import time
from typing import List, Dict

from config import DEFAULT_GOAL, MAX_PRICE, SIZES, BRANDS, SCRAPE_MAX_ITEMS, SLEEP_BETWEEN_LISTINGS
from planner import make_plan
from scraper import PoshmarkScraper
from evaluator import evaluate_listing
from scoring import compute_score
from memory import init_db, upsert_listing
from notifier import send_slack


THRESHOLD = 0.72  # decide threshold for good find


def run_cycle(goal: str, max_items: int, max_price: float, sizes: List[str], brands: List[str], stop_after:int|None=None) -> int:
    """Returns number of new good finds this cycle."""
    steps = make_plan(goal)

    # fetch
    scraper = PoshmarkScraper(sizes=sizes, brands=brands)
    listings = scraper.fetch(max_items=max_items)

    new_good = []

    for item in listings:
        price_str = item.get("price", "")
        # evaluate with vision
        vision = evaluate_listing(item["image_url"], item["title"], price_str)

        # enforce cap
        if vision.get("listed_price", 9999) > max_price:
            continue

        # score
        scored = compute_score(item, vision)
        score = scored["score"]

        record = {
            **item,
            "price": vision.get("listed_price", 0),
            "price_str": price_str,
            "vision": vision,
            "score": score,
            "brand_detected": scored.get("brand_detected", ""),
        }

        # persist (used also for dedupe — DB has uq on url)
        is_new = upsert_listing(record)

        if score >= THRESHOLD and is_new:
            new_good.append(record)

        time.sleep(SLEEP_BETWEEN_LISTINGS)

        if stop_after and len(new_good) >= stop_after:
            break

    # notify
    send_slack(sorted(new_good, key=lambda x: x["score"], reverse=True))

    return len(new_good)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic suit finder")
    parser.add_argument("--goal", default=DEFAULT_GOAL)
    parser.add_argument("--max-items", type=int, default=SCRAPE_MAX_ITEMS)
    parser.add_argument("--max-price", type=float, default=MAX_PRICE)
    parser.add_argument("--sizes", default=",".join(SIZES))
    parser.add_argument("--brands", default=",".join(BRANDS))

    # run modes
    parser.add_argument("--interval-min", type=int, default=0, help="If >0, loop every N minutes")
    parser.add_argument("--stop-after", type=int, default=0, help="Stop after N new good finds in a single run")

    args = parser.parse_args()

    sizes = [s.strip() for s in args.sizes.split(",") if s.strip()]
    brands = [b.strip() for b in args.brands.split(",") if b.strip()]

    init_db()

    if args.interval_min > 0:
        while True:
            try:
                run_cycle(
                    goal=args.goal,
                    max_items=args.max_items,
                    max_price=args.max_price,
                    sizes=sizes,
                    brands=brands,
                    stop_after=(args.stop_after or None),
                )
            except Exception as e:
                print("[cycle error]", e)
            finally:
                time.sleep(args.interval_min * 60)
    else:
        run_cycle(
            goal=args.goal,
            max_items=args.max_items,
            max_price=args.max_price,
            sizes=sizes,
            brands=brands,
            stop_after=(args.stop_after or None),
        )
