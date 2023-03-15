import pandas as pd
import re
import requests

from bs4 import BeautifulSoup
from datetime import date, timedelta
from weatherbit.api import Api

from category_constants import HISTORICAL_WEATHER_AVG_TITLE

MONTH_MAPPING = [
    'january',
    'february',
    'march',
    'april',
    'may',
    'june',
    'july',
    'august',
    'september',
    'october',
    'november',
    'december',
]

MONTH_ABV_MAPPING = [
    'Jan', 'Feb', 'Mar', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
]

COUNTRY_MAPPING = {'england': 'united_kingdom'}

WW_URL = "https://world-weather.info/forecast/{}/{}/{}-{}/"
WIKI_URL = "https://en.wikipedia.org/wiki/List_of_cities_by_average_temperature"


# http://www.city-data.com/forum/weather/2237356-what-do-people-consider-above-warm-3.html
def get_weather_type(temp: int, weather: str) -> str:
    """Get weather category from temperature and weather description.

    Parameters
    ----------
    temp : int
    weather : str

    Returns
    -------
    str
        Returns 'Really Cold', 'Cold', 'Chilly', 'Mild', 'Warm', or 'Hot'.
    """
    if 'rain' in weather.lower():
        return 'Rainy'

    if temp > 85:
        return 'Hot'
    # If between 80-85, or between 70-80 and not cloudy
    if (temp > 80) or (temp > 70 and ('cloud' not in weather.lower())):
        return 'Warm'
    # If between 65-70, or between 70-80 and cloudy
    if temp > 65:
        return 'Mild'
    if temp > 55:
        return 'Chilly'
    if temp > 32:
        return 'Cold'
    return 'Really Cold'


def celsius_to_fahrenheit(c):
    return c * 1.8 + 32


def get_monthly_weather_average(city: str, month: int):
    """Webscrape the monthly temperature average from Wikipedia page.

    Parameters
    ----------
    city : str
    month : int

    Returns
    -------
    float
    """
    numerical_inside_paren_regex = r"\(([\d.]+)\)"

    page = requests.get(WIKI_URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    tables = soup.find_all("table")

    for table in tables:
        df = pd.read_html(str(table))[0]

        df['City'] = df['City'].apply(lambda x: x.lower())
        if city in df['City'].values:
            weather_avgs = df[df['City'] == city]

            if len(weather_avgs) > 1:
                print('WARNING: there are multiple cities with the same name.')
                weather_avgs = weather_avgs[0]

            weather_avg = weather_avgs[MONTH_ABV_MAPPING[month + 1]].values[0]
            match = re.search(numerical_inside_paren_regex, weather_avg)
            return float(match.group(1))


def init_weather_info_dict() -> dict:
    return {'temps': [], 'weathers': [], 'weather_types': []}


def get_weather_from_api(city: str) -> dict:
    """Accesses the weather API to extract weather forecast 7 days out.

    Parameters
    ----------
    city : str

    Returns
    -------
    Dict[str, list]
      Dict with keys ('temps', 'weathers', 'weather_types'). Each contain lists
      of length 7.
    """
    API_KEY = 'caa03675924b4ef594b6c10289f02163'
    base_url = 'https://api.weatherbit.io/v2.0/forecast/daily'
    api_url = f'{base_url}?city={city}&key={API_KEY}'

    print(f"Accessing {api_url}...")
    response = requests.get(api_url)

    # If access to API is not granted, return empty `weather_info` dict.
    if response.status_code != 200:
        return init_weather_info_dict()

    # Take average of min and max temps.
    temps = []
    weathers = []
    weather_types = []
    for data in response.json()['data']:
        temp = (data['min_temp'] + data['max_temp']) / 2
        f_temp = celsius_to_fahrenheit(temp)
        weather = data['weather']['description']

        temps.append(round(f_temp, 2))
        weathers.append(weather)
        weather_types.append(get_weather_type(f_temp, weather))

    return {'temps': temps, 'weathers': weathers, 'weather_types': weather_types}


def get_webscaped_world_weather_data(year, month, country, city):
    """Get all sections from world weather html data with weather information.
    """
    country = COUNTRY_MAPPING.get(country, country)
    weather_url = WW_URL.format(
        country, city.replace(' ', '_'), MONTH_MAPPING[month - 1], year,
    )
    page = requests.get(weather_url)

    # If world weather request gives access to enter, webscrape weather data.
    if page.status_code != 200:
        return

    class_regex = 'ww-month-week(end|days) (fore(a|)cast)(-statistics|)(-archive)'

    soup = BeautifulSoup(page.content, 'html.parser')
    return soup.find_all(True, {'class': re.compile(class_regex)})


def get_temp_from_world_weather_month_html(sections, current_date):
    weather_class_regex = 'icon-weather wi d\d{3} tooltip'

    # This iterates through the days of the month from the html code.
    for x in sections:
        # If the section date is the date we're interested in, return info.
        if int(x.div.text) == int(current_date.day):
            weather = x.find(True, {'class': re.compile(weather_class_regex)}).get('title')
            temp = int(x.span.text.replace('+', '').replace('°', ''))

            return temp, weather, get_weather_type(temp, weather)


def get_projected_weather(
    start_date, end_date, city: str, country: str
) -> dict:
    """Get projected weather from `start_date` to `end_date`.

    Returns the projected temperature, weather description (e.g. 'Cloudy with
    scattered rain'), and weather type (e.g. 'Chilly').

    Uses weather API if available. If not, tries to webscrape data from World
    Weather site. If site does not grant access, uses historical temperature
    averages that are provided from the wikipedia page.

    Parameters
    ----------
    start_date : datetime.date
    end_date : datetime.date
    city : str
    country : str

    Returns
    -------
    dict
        Returns dict of lists with keys ('temps', 'weathers', 'weather_types').
    """
    # Get data from the weather api for as many days as possible.
    # The api provides forecast up to 7 days ahead.
    weather_info = get_weather_from_api(city)

    # Get the indices of which dates from today to up to 7 days overlap with
    # the timeframe between `start_date` and `end_date`.
    inds = []
    weather_info_dates = [date.today() + timedelta(days=i) for i in range(7)]
    for i, weather_date in enumerate(weather_info_dates):
        if weather_date >= start_date and weather_date <= end_date:
            inds.append(i)

    # Update `weather_info` to only include information from the dates within
    # the timeframe from `start_date` to `end_date`.
    if not inds:
        weather_info = init_weather_info_dict()
    else:
        for key in weather_info:
            weather_info[key] = weather_info[key][min(inds):max(inds)+1]

    num_days_accessed = len(weather_info['temps'])

    timeperiod = (end_date - start_date).days + 1
    if timeperiod < num_days_accessed:
        for key in ['temps', 'weathers', 'weather_types']:
            weather_info[key] = weather_info[key][:timeperiod]

        return weather_info

    # Update `start_date` to be date where weather information still needs to
    # be gathered.
    start_date = start_date + timedelta(days=num_days_accessed)

    # Iterate through days to extract appropriate weather info for that day.
    current_month = start_date.month
    for day in range((end_date - start_date).days + 1):
        current_date = start_date + timedelta(days=1) * day

        # Don't recalculate monthly forecasts if it's the same month.
        if (day == 0) or (current_month != current_date.month):
            # Try webscraping the world weather site first.
            ww_sections = get_webscaped_world_weather_data(
                current_date.year, current_date.month, country, city
            )

            # If access to weather site not granted, use wikipedia-provided
            # monthly avgs.
            if not ww_sections:
                print('Access to World Weather site not granted.')
                monthly_avg = get_monthly_weather_average(city, current_date.month)
                current_month = current_date.month

        if ww_sections:
            temp, weather, weather_type = (
                get_temp_from_world_weather_month_html(ww_sections, current_date)
            )
        else:
            temp = monthly_avg
            weather = HISTORICAL_WEATHER_AVG_TITLE
            weather_type = get_weather_type(monthly_avg, 'unknown')

        weather_info['temps'].append(temp)
        weather_info['weathers'].append(weather)
        weather_info['weather_types'].append(weather_type)

    return weather_info
