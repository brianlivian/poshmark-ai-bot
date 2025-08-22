from dataclasses import dataclass
from typing import List

@dataclass
class PlanStep:
    name: str
    description: str

def make_plan(goal: str) -> List[PlanStep]:
    return [
        PlanStep("fetch", "Scrape sites for candidate listings"),
        PlanStep("dedupe", "Remove listings already seen in DB"),
        PlanStep("evaluate", "Use vision to judge style/condition/fit & price"),
        PlanStep("score", "Blend vision verdict with heuristics and price cap"),
        PlanStep("decide", "Pick top items above threshold"),
        PlanStep("notify", "Send Slack alert if new winners found"),
    ]
