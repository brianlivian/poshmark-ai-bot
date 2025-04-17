# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.17.0
#   kernelspec:
#     display_name: .venv
#     language: python
#     name: python3
# ---

# +
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
client = OpenAI(api_key= os.getenv('openai_api'))

# +
URL = "https://poshmark.com/category/Men-Suits_&_Blazers-Suits?sort_by=added_desc&brand%5B%5D=All%20Saints&brand%5B%5D=Andrew%20Marc&brand%5B%5D=Armani%20Collezioni&brand%5B%5D=Banana%20Republic&brand%5B%5D=Barneys%20New%20York&brand%5B%5D=Boglioli&brand%5B%5D=Bonobos&brand%5B%5D=Brooks%20Brothers&brand%5B%5D=Burberry&brand%5B%5D=Canali&brand%5B%5D=Charles%20Tyrwhitt&brand%5B%5D=Club%20Monaco&brand%5B%5D=Corneliani&brand%5B%5D=Eleventy&brand%5B%5D=Emporio%20Armani&brand%5B%5D=Ermenegildo%20Zegna&brand%5B%5D=Etro&brand%5B%5D=Gucci&brand%5B%5D=Hart%20Schaffner%20Marx&brand%5B%5D=Hickey%20Freeman&brand%5B%5D=Hugo%20Boss&brand%5B%5D=Isaia&brand%5B%5D=Jack%20Victor&brand%5B%5D=John%20Varvatos&brand%5B%5D=Joseph%20Abboud&brand%5B%5D=Kiton&brand%5B%5D=Lardini&brand%5B%5D=Lubiam&brand%5B%5D=Luciano%20Barbera&brand%5B%5D=Massimo%20Dutti&brand%5B%5D=Pal%20Zileri&brand%5B%5D=Paul%20Smith&brand%5B%5D=Paul%20Stuart&brand%5B%5D=Ralph%20Lauren&brand%5B%5D=Ralph%20Lauren%20Black%20Label&brand%5B%5D=Ralph%20Lauren%20Blue%20Label&brand%5B%5D=Ralph%20Lauren%20Double%20RL&brand%5B%5D=Ralph%20Lauren%20Purple%20Label&brand%5B%5D=Reiss&brand%5B%5D=Robert%20Talbott&brand%5B%5D=Sandro&brand%5B%5D=SuitSupply&brand%5B%5D=Ted%20Baker&brand%5B%5D=Theory&brand%5B%5D=Topman%22&size%5B%5D=44R&size%5B%5D=43R&size%5B%5D=42R"

def get_listing_info_with_selenium(url, max_items=10):
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "img")))

    scroll_pause_time = 2
    last_height = driver.execute_script("return document.body.scrollHeight")

    for _ in range(10):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    listings = driver.find_elements(By.CSS_SELECTOR, 'div[data-et-name="listing"]')
    listing_info = []

    for card in listings:
        try:
            img = card.find_element(By.TAG_NAME, "img")
            src = img.get_attribute("src")

            anchor = card.find_element(By.TAG_NAME, "a")
            listing_url = anchor.get_attribute("href")

            text_elements = card.find_elements(By.TAG_NAME, "div")
            title = ""
            price = ""
            for el in text_elements:
                txt = el.text.strip()
                if "$" in txt and not price:
                    price = txt
                elif txt and not title:
                    title = txt
            title = title.split('\n')[0]
            price = price.split('\n')[1].split(' ')[0]

            listing_info.append({
                "image_url": src,
                "title": title,
                "price": price,
                "url": listing_url
            })

        except Exception as e:
            print("Error extracting listing:", e)
            continue

        if len(listing_info) >= max_items:
            break

    driver.quit()
    return listing_info


def check_suit_appropriateness(image_url, brand, price):
    # print(brand, price, 'Brian Rocks')
    prompt = (
        f"This is a listing for a men's clothing item from the brand '{brand}', priced at '{price}'. "
        f"The brand is already known to be high-quality and fashionable. "
        f"Please analyze whether the item looks modern, stylish, and sharp — something a young professional in his 20s or 30s would wear "
        f"to a social event, date, work setting, or while going out. It should have a good fit (not overly baggy or outdated), be in good condition, and appear well-made. "
        f"Also determine whether the listed price is a good deal (e.g., a designer or great-looking item for under $150). "
        f"Only answer 'yes' if the clothing looks stylish, appropriate for a modern young professional, and priced well. Otherwise, answer 'no'."
    )





    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "synagogue_suit_check",
                    "description": "Returns 'yes' only if the suit is from a luxury brand, is very stylish and appropriate for synagogue, and is being sold at a low price.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "answer": {
                                "type": "string",
                                "enum": ["yes", "no"]
                            }
                        },
                        "required": ["answer"]
                    }
                }
            }
        ],
        tool_choice={"type": "function", "function": {"name": "synagogue_suit_check"}},
        max_tokens=500
    )

    tool_call = response.choices[0].message.tool_calls[0]
    result = json.loads(tool_call.function.arguments)
    return result["answer"]


data = pd.DataFrame(columns = ['Listing Title', 'Price', 'URL', 'Image', 'AI Verdict'])

# --- Main Run ---
if __name__ == "__main__":
    print("Scraping listings...")
    listings = get_listing_info_with_selenium(URL, max_items=10)
    print(f"\n✅ Found {len(listings)} listings. Evaluating...\n")

    for i, listing in enumerate(listings):
        try:
            df = pd.DataFrame()
            answer = check_suit_appropriateness(
                listing["image_url"],
                brand=listing["title"],
                price=listing["price"]
            )
            df['Listing Title'] = [listing['title']]
            df ['Price'] = [listing['price']]
            df['Image'] = [listing['image_url']]
            df['URL'] = [listing['url']]
            df['AI Verdict'] =[ answer.upper()]
            data = pd.concat([data,df])

            time.sleep(1)
        except Exception as e:
            print(f"[{i+1}] ERROR – {e}")


# -

pd.set_option('display.max_colwidth', None)
data


