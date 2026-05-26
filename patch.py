import re

def update_script():
    with open('scraper.py', 'r') as f:
        content = f.read()

    # On ajoute des mots-clés pour exclure le foot
    new_exclusions = '["包", "bag", "眼镜", "sunglasses", "帽", "hat", "cap", "皮带", "belt", "耳机", "headphones", "earbuds", "case", "香水", "keychain", "音箱", "speaker", "项链", "戒指", "手链", "retro", "home", "away", "jersey", "chelsea", "arsenal", "manchester", "tottenham", "aston villa", "newcastle", "champions league", "m-u"]'

    # On retire 'home' et 'away' des inclusions s'ils y étaient
    new_inclusions = '["t-shirt", "tee", "shirt", "hoodie", "shoes", "sneaker", "jacket", "pants", "jean", "short", "sweater", "外套", "裤", "短袖", "长袖", "鞋", "马甲", "西装", "连体衣", "polo"]'

    # Remplacement
    content = re.sub(r'exclusions = \[.*?\]', f'exclusions = {new_exclusions}', content)
    content = re.sub(r'inclusions = \[.*?\]', f'inclusions = {new_inclusions}', content)

    with open('scraper.py', 'w') as f:
        f.write(content)

update_script()
