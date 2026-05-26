import re

titles = [
    "¥31 lili-56777800",
    "￥99 wanban-Retro Manchester City 13/14 Home S-XXL",
    "￥455/460 660523104 xinxin托特包，25/35cm",
    "¥168外套 ¥158裤子 Nanyi-660514179",
    "230-zhenhui-adidas",
    "没有价格的衣服 S-XL"
]

for title in titles:
    price_match = re.search(r'[¥￥]\s*(\d+)', title)
    if price_match:
        print(f"Title: {title} -> Price: {price_match.group(1)}")
    else:
        print(f"Title: {title} -> Price: Not found")
