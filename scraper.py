import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import os

BASE_URL = "https://3125tiger.x.yupoo.com/albums?tab=gallery&page="
ALBUM_BASE_URL = "https://3125tiger.x.yupoo.com"
IMAGES_DIR = "images"

if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

def get_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://3125tiger.x.yupoo.com/"
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
        "Referer": "https://3125tiger.x.yupoo.com/"
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
    price_match = re.search(r'[¥￥]\s*(\d+)', title)
    if price_match:
        return price_match.group(1) + ".00"
    return "0.00"

def is_clothing_or_shoes(title):
    lower_title = title.lower()
    exclusions = ["包", "bag", "眼镜", "sunglasses", "帽", "hat", "cap", "皮带", "belt", "耳机", "headphones", "earbuds", "case", "香水", "keychain", "音箱", "speaker", "项链", "戒指", "手链", "retro", "home", "away", "jersey", "chelsea", "arsenal", "manchester", "tottenham", "aston villa", "newcastle", "champions league", "m-u"]
    for ex in exclusions:
        if ex in lower_title:
            return False

    inclusions = ["t-shirt", "tee", "shirt", "hoodie", "shoes", "sneaker", "jacket", "pants", "jean", "short", "sweater", "外套", "裤", "短袖", "长袖", "鞋", "马甲", "西装", "连体衣", "polo"]
    for inc in inclusions:
        if inc in lower_title:
            return True

    if re.search(r'([SMLX]{1,3})\s*-\s*([SMLX]{1,3})', title.upper()):
        return True

    if re.search(r'\b(3[5-9]|4[0-8])\s*-\s*(3[5-9]|4[0-8])\b', title):
        return True

    return False

def main():
    target_count = 500
    products = []
    page = 1

    print("Starting scraping...")

    while len(products) < target_count:
        print(f"Scraping page {page}...")
        url = BASE_URL + str(page)
        soup = get_soup(url)

        if not soup:
            print(f"Failed to fetch page {page}")
            break

        albums = soup.find_all('a', class_='album__main')
        if not albums:
            print("No albums found on page, ending loop.")
            break

        for album in albums:
            if len(products) >= target_count:
                break

            title = album.get('title', '').strip()

            # Filtre : on ne garde que vêtements et chaussures
            if not is_clothing_or_shoes(title):
                continue

            img = album.find('img')
            img_src = ""
            local_img_path = ""
            if img:
                img_src = img.get('data-src') or img.get('src')
                if img_src and img_src.startswith('//'):
                    img_src = "https:" + img_src

            handle = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

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

            print(f"Scraped: {title} (Price: ¥{price}) ({len(products)}/{target_count})")

        page += 1

    print(f"Scraped {len(products)} products.")

    # Generate simple CSV
    df = pd.DataFrame(products)
    df.to_csv('yupoo_produits_500.csv', index=False)
    print("CSV saved as yupoo_produits_500.csv")
    print(f"Images downloaded in {IMAGES_DIR}/ directory.")

if __name__ == "__main__":
    main()
