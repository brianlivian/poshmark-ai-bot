from __future__ import annotations
import time
import urllib.parse as up
from typing import Dict, List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from config import HEADLESS

POSH_BASE = "https://poshmark.com/category/Men-Suits_&_Blazers-Suits"


class PoshmarkScraper:
    def __init__(self, sizes: List[str], brands: List[str], sort="added_desc"):
        self.sizes = sizes
        self.brands = brands
        self.sort = sort

    def build_url(self) -> str:
        qs = []
        if self.sort:
            qs.append(("sort_by", self.sort))
        for b in self.brands:
            qs.append(("brand[]", b))
        for s in self.sizes:
            qs.append(("size[]", s))
        return f"{POSH_BASE}?" + up.urlencode(qs, doseq=True)

    def _driver(self):
        opts = Options()
        if HEADLESS:
            opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--user-agent=Mozilla/5.0 AgenticSuitFinder")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=opts)

    def fetch(self, max_items=60) -> List[Dict]:
        url = self.build_url()
        driver = self._driver()
        driver.get(url)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "img"))
        )

        # scroll to load
        last_h = 0
        for _ in range(12):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
            new_h = driver.execute_script("return document.body.scrollHeight")
            if new_h == last_h:
                break
            last_h = new_h
            if _ * 20 >= max_items:
                break

        # try multiple selectors for resilience
        selectors = [
            'div[data-et-name="listing"]',  # canonical
            'li.tile',                        # fallback
            'div.card.card--small'            # fallback 2
        ]

        cards = []
        for sel in selectors:
            cards = driver.find_elements(By.CSS_SELECTOR, sel)
            if cards:
                break

        results = []
        for c in cards:
            try:
                a = c.find_element(By.TAG_NAME, "a")
                href = a.get_attribute("href")
                img = c.find_element(By.TAG_NAME, "img")
                src = img.get_attribute("src")

                # Try to extract text blocks
                texts = [x.text.strip() for x in c.find_elements(By.TAG_NAME, "div") if x.text.strip()]
                title = texts[0] if texts else ""

                # Find a price block containing '$'
                price = ""
                for t in texts:
                    if "$" in t:
                        # Many poshmark cards render like: "$120  $300  Size 42R"
                        price = t.split("$")[1].split()[0]
                        price = f"${price}"
                        break

                results.append({
                    "title": title,
                    "price": price,
                    "url": href,
                    "image_url": src,
                    "source": "poshmark",
                })
                if len(results) >= max_items:
                    break
            except Exception:
                continue

        driver.quit()
        return results
