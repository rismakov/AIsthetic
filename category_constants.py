MAIN_CATEGORIES = ['tops', 'bottoms', 'dresses', 'outerwear', 'shoes']
ACCESSORIES = ['hats', 'bags']

ALL_CATEGORIES = MAIN_CATEGORIES + ACCESSORIES

OCCASION_TAGS = {
    'Casual': 'ca_',
    'Work': 'wo_',
    'Dinner/Bar': 'bar_',
    'Club/Fancy': 'f_',
}

SEASON_TAGS = {
    'Summer': 'su_',
    'Fall': 'fa_',
    'Winter': 'wi_',
    'Spring': 'sp_',
}

STYLE_TAGS = {
    'Basic': 'bas_',
    'Statement': 'st_',
}

WEATHER_ICON_MAPPING = {
    'Partly cloudy': 'partly_cloudy.png',
    'Clear': 'sunny.png',
    'Mostly clear': 'sunny.png',
    'Cloudy': 'cloudy.png',
    'Rainy': 'rainy.png',
    'Really Cold': 'cold.png',
}

WEATHER_TO_SEASON_MAPPINGS = {
    'Hot': 'Summer',
    'Warm': 'Summer',
    'Mild': 'Spring',
    'Chilly': 'Fall',
    'Rainy': 'Fall',
    'Cold': 'Winter',
    'Really Cold': 'Winter',
}

_high_cadence = {
    'tops': 4,
    'bottoms': 4,
    'dresses': 4,
    'outerwear': 0,
}

_med_cadence = {
    'tops': 5,
    'bottoms': 5,
    'dresses': 6,
    'outerwear': 1,
}

_low_cadence = {
    'tops': 6,
    'bottoms': 6,
    'dresses': 9, 
    'outerwear': 3,
} 

CADENCES = {
    'small carry-on suitcase': _high_cadence,
    'medium suitcase': _med_cadence,
    'entire closet': _low_cadence,
}
