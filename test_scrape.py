import re

def get_sizes(title):
    # Try to find S-XXL or similar size ranges in title
    title_upper = title.upper()
    size_range_match = re.search(r'([SMLX]{1,3})\s*-\s*([SMLX]{1,3})', title_upper)
    sizes = ["S", "M", "L", "XL"] # Default

    if size_range_match:
        start_size = size_range_match.group(1)
        end_size = size_range_match.group(2)
        # simplified size generation based on common ranges
        all_sizes = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]
        if start_size in all_sizes and end_size in all_sizes:
            start_idx = all_sizes.index(start_size)
            end_idx = all_sizes.index(end_size)
            if start_idx <= end_idx:
                sizes = all_sizes[start_idx:end_idx+1]

    # Check for shoes sizes, e.g. 36-45
    shoe_size_match = re.search(r'(\d{2})\s*-\s*(\d{2})', title)
    if shoe_size_match:
        start_size = int(shoe_size_match.group(1))
        end_size = int(shoe_size_match.group(2))
        if 35 <= start_size <= 48 and 35 <= end_size <= 48 and start_size <= end_size:
            sizes = [str(s) for s in range(start_size, end_size + 1)]

    return sizes

print(get_sizes("￥99 wanban-Retro Manchester City 13/14 Home S-XXL"))
print(get_sizes("NK Shoes 36-45"))
