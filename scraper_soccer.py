import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import os

BASE_URL = "https://kingsoccerjerseys.x.yupoo.com/categories/5150555?page="
ALBUM_BASE_URL = "https://kingsoccerjerseys.x.yupoo.com"
IMAGES_DIR = "images_soccer"

if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

def get_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://kingsoccerjerseys.x.yupoo.com/"
    }
    for _ in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            time.sleep(1)
    return None

def download_image(img_url, filename):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://kingsoccerjerseys.x.yupoo.com/"
    }
    try:
        response = requests.get(img_url, headers=headers, timeout=10, stream=True)
        if response.status_code == 200:
            filepath = os.path.join(IMAGES_DIR, filename)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return filepath
    except Exception as e:
        print(f"Failed to download {img_url}: {e}")
    return None

def extract_price(title):
    price_match = re.search(r'[¥￥$€]\s*(\d+)', title)
    if price_match:
        return price_match.group(1) + ".00"
    return ""

def is_men_item(title):
    lower_title = title.lower()
    # Exclude women and kids
    exclusions = ["women", "woman", "ladies", "fille", "femme", "kids", "kid", "youth", "child", "children", "enfant", "garçon", "baby", "toddler"]
    for ex in exclusions:
        if ex in lower_title:
            return False

    # Include only if it seems like a jersey or shorts (optional, but good to filter out random stuff)
    # The user asked for soccer jerseys, and explicitly to exclude kids/women.
    # Usually, if it doesn't specify women/kids on a soccer yupoo, it's a men's size.
    return True

def main():
    products = []
    page = 1

    print("Starting scraping for King Soccer Jerseys...")

    while True:
        print(f"Scraping page {page}...")
        url = BASE_URL + str(page)
        soup = get_soup(url)

        if not soup:
            print(f"Failed to fetch page {page}")
            break

        albums = soup.find_all('a', class_='album__main')
        if not albums:
            print("No more albums found, ending loop.")
            break

        for album in albums:
            title = album.get('title', '').strip()

            if not is_men_item(title):
                print(f"Skipped (Women/Kids): {title}")
                continue

            img = album.find('img')
            img_src = ""
            local_img_path = ""
            if img:
                img_src = img.get('data-src') or img.get('src')
                if img_src and img_src.startswith('//'):
                    img_src = "https:" + img_src

            base_handle = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
            handle = f"{base_handle}-{len(products)}"

            # Download image
            if img_src:
                ext = img_src.split('.')[-1].split('?')[0]
                if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                    ext = 'jpg'
                filename = f"{handle}.{ext}"
                local_path = download_image(img_src, filename)
                if local_path:
                    local_img_path = local_path

            price = extract_price(title)

            products.append({
                "Titre": title,
                "Prix": price,
                "URL Image": img_src,
                "Chemin Local Image": local_img_path
            })

            print(f"Scraped: {title} ({len(products)} found so far)")

        page += 1

    print(f"Scraped a total of {len(products)} products.")

    # Generate simple CSV
    df = pd.DataFrame(products)
    df.to_csv('kingsoccer_produits.csv', index=False)
    print("CSV saved as kingsoccer_produits.csv")
    print(f"Images downloaded in {IMAGES_DIR}/ directory.")

if __name__ == "__main__":
    main()
