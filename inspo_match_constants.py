# These are labels that the Google Vision API returns
MATCH_GROUPS = {
    'skirts': ("skirt", "miniskirt"), 
    'pants': ("jeans", "pants", 'trousers'), 
    'shorts': ("shorts"),
    'jackets': ("jacket", "vest", "outerwear", "coat", "suit", 'blazer', 'overcoat'),
    'shirts': ("top", "shirt", 'jersey', 'tops'),
    'dresses': ("dress", 'dresses'),
    'swimwear': ("swimwear", "underpants"),
    'shoes': ("footwear", "sandal", "boot", "high heels", 'shoe', 'shoes'),
    'bags': ("handbag", "suitcase", "satchel", "backpack", "briefcase", 'bag', 'luggage and bags', 'bags'),
    'sunglasses': ("sunglasses", "glasses", 'eyewear'),
    'scarfs': ("scarf", "bowtie", "tie"),
    'hats': ("hat", "cowboy hat", "straw hat", "fedora", "sun hat", "sombrero", 'helmet', 'hats'),
}

# These are labels that the closet set products have been categorized into
CATEGORIES = {
    'tops': {'shirts'},
    'bottoms': {'skirts', 'pants', 'shorts'},
    'outerwear': {'jackets'},
    'dresses': {'dresses'},
    'shoes': {'shoes'},
    'bags': {'bags'},
    'hats': {'hats'},
}
