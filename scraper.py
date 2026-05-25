import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import urllib.parse
import os

BASE_URL = "https://3125tiger.x.yupoo.com/albums?tab=gallery&page="
ALBUM_BASE_URL = "https://3125tiger.x.yupoo.com"

def get_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    for _ in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            time.sleep(1)
    return None

def extract_vendor_type(title):
    vendor = "3125tiger"
    product_type = "Apparel"

    lower_title = title.lower()
    if "t-shirt" in lower_title or "tee" in lower_title:
        product_type = "T-Shirt"
    elif "shirt" in lower_title:
        product_type = "Shirt"
    elif "hoodie" in lower_title:
        product_type = "Hoodie"
    elif "shoes" in lower_title or "sneaker" in lower_title:
        product_type = "Shoes"
    elif "jacket" in lower_title:
        product_type = "Jacket"
    elif "pants" in lower_title or "jean" in lower_title:
        product_type = "Pants"
    elif "bag" in lower_title:
        product_type = "Bag"
    elif "short" in lower_title:
        product_type = "Shorts"
    elif "sweater" in lower_title:
        product_type = "Sweater"

    parts = title.split(' ')
    if len(parts) > 1:
        # Ignore price like ¥31 or ￥99
        cleaned_parts = [p for p in parts if not re.match(r'^[¥￥\d]+$', p)]
        if cleaned_parts:
            # Usually the first word after the price might indicate the batch or brand
            potential_vendor = cleaned_parts[0]
            if '-' in potential_vendor:
                # sometimes it's format like lili-56777800, maybe the part before or after is brand
                potential_vendor = potential_vendor.split('-')[0]
            if len(potential_vendor) > 1:
                vendor = potential_vendor.capitalize()

    return vendor, product_type

def get_sizes(title, product_type):
    title_upper = title.upper()
    size_range_match = re.search(r'([SMLX]{1,3})\s*-\s*([SMLX]{1,3})', title_upper)
    sizes = ["S", "M", "L", "XL"]

    if product_type == "Shoes":
        sizes = ["39", "40", "41", "42", "43", "44", "45"] # Default shoe sizes
        shoe_size_match = re.search(r'(\d{2})\s*-\s*(\d{2})', title)
        if shoe_size_match:
            start_size = int(shoe_size_match.group(1))
            end_size = int(shoe_size_match.group(2))
            if 35 <= start_size <= 48 and 35 <= end_size <= 48 and start_size <= end_size:
                sizes = [str(s) for s in range(start_size, end_size + 1)]
    else:
        if size_range_match:
            start_size = size_range_match.group(1)
            end_size = size_range_match.group(2)
            all_sizes = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]
            if start_size in all_sizes and end_size in all_sizes:
                start_idx = all_sizes.index(start_size)
                end_idx = all_sizes.index(end_size)
                if start_idx <= end_idx:
                    sizes = all_sizes[start_idx:end_idx+1]

    return sizes

def main():
    target_count = 200
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
            href = album.get('href', '')
            album_url = ALBUM_BASE_URL + href if href.startswith('/') else href

            img = album.find('img')
            img_src = ""
            if img:
                img_src = img.get('data-src') or img.get('src')
                if img_src and img_src.startswith('//'):
                    img_src = "https:" + img_src

            # Get description by visiting the album page
            description = ""
            album_soup = get_soup(album_url)
            if album_soup:
                desc_tag = album_soup.find('div', class_='showalbumheader__gallerysubtitle')
                if desc_tag:
                    description = desc_tag.text.strip()

            vendor, product_type = extract_vendor_type(title)
            sizes = get_sizes(title, product_type)
            handle = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

            products.append({
                "Handle": handle,
                "Title": title,
                "Body (HTML)": f"<p>{description}</p>" if description else "",
                "Vendor": vendor,
                "Product Category": product_type,
                "Type": product_type,
                "Tags": f"{vendor}, {product_type}",
                "Published": "TRUE",
                "Option1 Name": "Size",
                "Option1 Values": sizes,
                "Variant Price": "199.00",
                "Image Src": img_src,
                "Image Position": 1,
                "Status": "active"
            })

            print(f"Scraped: {title} ({len(products)}/{target_count})")

        page += 1

    print(f"Scraped {len(products)} products.")

    # Generate Shopify CSV
    rows = []
    for p in products:
        # First row for the product includes title, desc, vendor, etc. and the first variant
        first_variant = True
        for size in p["Option1 Values"]:
            row = {
                "Handle": p["Handle"],
                "Title": p["Title"] if first_variant else "",
                "Body (HTML)": p["Body (HTML)"] if first_variant else "",
                "Vendor": p["Vendor"] if first_variant else "",
                "Product Category": p["Product Category"] if first_variant else "",
                "Type": p["Type"] if first_variant else "",
                "Tags": p["Tags"] if first_variant else "",
                "Published": p["Published"] if first_variant else "",
                "Option1 Name": p["Option1 Name"],
                "Option1 Value": size,
                "Variant Inventory Tracker": "shopify",
                "Variant Inventory Qty": "100",
                "Variant Inventory Policy": "continue",
                "Variant Fulfillment Service": "manual",
                "Variant Price": p["Variant Price"],
                "Variant Requires Shipping": "TRUE",
                "Variant Taxable": "TRUE",
                "Image Src": p["Image Src"] if first_variant else "",
                "Image Position": p["Image Position"] if first_variant else "",
                "Status": p["Status"] if first_variant else ""
            }
            rows.append(row)
            first_variant = False

    df = pd.DataFrame(rows)
    df.to_csv('yupoo_shopify_import.csv', index=False)
    print("CSV saved as yupoo_shopify_import.csv")

if __name__ == "__main__":
    main()
