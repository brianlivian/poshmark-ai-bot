# 🧥 Agentic AI Clothing Evaluator

An **agentic** fashion assistant that plans, executes, and learns while hunting premium men’s clothing on Poshmark. It scrapes new listings, uses **GPT-4o Vision** to judge style/condition from images, blends in heuristics (brand, size, price), remembers what it’s seen, and **notifies you** when a great find appears.

**Built with:** Python · OpenAI API · GPT-4o Vision · Selenium · Pandas · SQLite · Slack/Webhook Alerts

---

## Why “agentic”?
This isn’t a one-off script—it’s a small **planner + executor** that runs in cycles:

1. **Fetch** – adaptive Selenium scraper (fallback selectors, headless/visible).  
2. **Dedupe** – SQLite memory tracks seen URLs & updates.  
3. **Evaluate** – GPT-4o Vision scores modernity, style, condition, and price sanity.  
4. **Score** – multi-criteria blend (brand priors, size match, condition hints, price vs cap).  
5. **Decide** – thresholded picks (e.g., score ≥ 0.72).  
6. **Notify** – Slack (or email/SMS) with title, score, price, image, and link.  
7. **Repeat** – run on an interval; guardrails for rate/budget.

The agent also supports **memory & persistence**, **user-taste hooks** (brand/cut boosts), **scheduling**, and **guardrails** (rate limiting, budget cap, no-buy by default).

---

## ✨ Features
- **Goal-driven**: “Find modern suits under $150 in sizes 42–44R and alert me.”  
- **Planner + Executor**: deterministic loop with clear steps.  
- **Adaptive scraping**: multiple CSS selectors, retry/backoff, headless toggle.  
- **Vision evaluation**: GPT-4o judges fit/modernity/condition from images.  
- **Multi-criteria scoring**: blends vision + metadata (brand, size, price, keywords).  
- **SQLite memory**: dedupe, track price/score over time.  
- **Notifications**: Slack webhooks by default (email/SMS easy to add).  
- **Scheduling**: run once or every N minutes.  
- **Guardrails**: polite crawling, rate limiting, budget caps, explicit “no-buy”.

---

## 🚀 Quick start
```bash
python3 -m venv .venv
source .venv/bin/activate                 # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                      # or create .env; add OPENAI_API_KEY & SLACK_WEBHOOK_URL
python main.py --max-items 20 --stop-after 2
