MAIN_CATEGORIES = ['tops', 'bottoms', 'dresses', 'outerwear', 'shoes']
ACCESSORIES = ['hats', 'bags']

ALL_CATEGORIES = MAIN_CATEGORIES + ACCESSORIES

OCCASIONS = ['Casual', 'Work', 'Dinner/Bar', 'Club/Fancy']
SEASONS = ['Summer', 'Fall', 'Winter', 'Spring']

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
    'top': 4,
    'bottom': 4,
    'dress': 4,
    'outerwear': 0,
}

_med_cadence = {
    'top': 5,
    'bottom': 5,
    'dress': 6,
    'outerwear': 1,
}

_low_cadence = {
    'top': 6,
    'bottom': 6,
    'dress': 9,
    'outerwear': 3,
}

OUTFIT_AMOUNT = {
    'small carry-on suitcase': 7,
    'medium suitcase': 12,
    'large suitcase': 20,
}

CADENCES = {
    'small carry-on suitcase': _high_cadence,
    'medium suitcase': _med_cadence,
    'large suitcase': _med_cadence,
    'entire closet': _low_cadence,
}
