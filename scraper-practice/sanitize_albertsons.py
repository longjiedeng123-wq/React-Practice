import re

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}

UOM_MAP = {
    "ea": "EA", "each": "EA",
    "lb": "LB", "lbs": "LB", "pound": "LB",
    "oz": "OZ", "ounce": "OZ",
    "bag": "BAG", 
    "bunch": "BUNCH",
    "dz": "DZ", "dozen": "DZ",
    "pk": "PK", "pack": "PK"
}

def parse_int_or_word(val: str) -> int:
    clean_val = val.strip().lower()
    if clean_val.isdigit():
        return int(clean_val)
    return NUMBER_WORDS.get(clean_val, 1)

def extract_unit(text: str) -> str:
    if not text:
        return None
    
    clean_text = text.lower()
    for key, standardized_unit in UOM_MAP.items():
        if re.search(rf'\b{key}\b', clean_text):
            return standardized_unit
            
    return None

def extract_constraints(text: str) -> dict:
    if not text:
        return {"min_qty_required": 1, "limit_qty": None}
    
    text = text.lower()
    
    min_qty_match = re.search(r'(?:buy|purchase|must buy|when you buy|with purchase of)\s*(\d+|one|two|three|four|five|six|seven|eight|nine|ten)', text)
    min_qty = parse_int_or_word(min_qty_match.group(1)) if min_qty_match else 1
    
    limit_match = re.search(r'(?:limit|limit of|maximum)\s*(\d+|one|two|three|four|five|six|seven|eight|nine|ten)', text)
    limit_qty = parse_int_or_word(limit_match.group(1)) if limit_match else None
    
    return {"min_qty_required": min_qty, "limit_qty": limit_qty}


def sanitize_albertsons_flipp_item(raw_item: dict) -> dict:
    name = raw_item.get("name")
    if not name:
        return {}
    
    price_str = raw_item.get("price_text")
    try:
        discount_price = float(price_str) if price_str else None
    except ValueError:
        discount_price = None

    valid_dates = f"{raw_item.get('valid_from')} to {raw_item.get('valid_to')}"
    
    promo_text = f"{raw_item.get('description') or ''} {raw_item.get('post_price_text') or ''} {raw_item.get('disclaimer_text') or ''}"
    constraints = extract_constraints(promo_text)
    
    return {
        "english_name": name,
        "chinese_name": None,
        "base_unit_type": extract_unit(raw_item.get("post_price_text")),
        "discount_price": discount_price,
        "original_price": raw_item.get("original_price"),
        "valid_dates": valid_dates,
        "min_qty_required": constraints["min_qty_required"],
        "limit_qty": constraints["limit_qty"],
        "taxable": False,
        "has_crv": False
    }

def sanitize_albertsons_j4u_item(raw_item: dict) -> dict:
    name = raw_item.get("brand")
    if not name:
        return {}
    
    price_str = raw_item.get("offerPrice", "")
    price_match = re.search(r'\$(\d+(?:\.\d{2})?)', price_str)
    discount_price = float(price_match.group(1)) if price_match else None

    start = raw_item.get("offerStartDate", "")[:10]
    end = raw_item.get("offerEndDate", "")[:10]
    valid_dates = f"{start} to {end}" if start and end else None
    
    promo_text = f"{raw_item.get('description', '')} {raw_item.get('details', '')}"
    constraints = extract_constraints(promo_text)
    
    return {
        "english_name": name,
        "chinese_name": None,
        "base_unit_type": extract_unit(promo_text),
        "discount_price": discount_price,
        "original_price": None, 
        "valid_dates": valid_dates,
        "min_qty_required": constraints["min_qty_required"],
        "limit_qty": constraints["limit_qty"],
        "taxable": False,
        "has_crv": False
    }