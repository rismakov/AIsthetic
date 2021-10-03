import re
import requests 

from bs4 import BeautifulSoup
from datetime import date, timedelta

MONTH_MAPPING = [
    'january', 
    'feburary', 
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

COUNTRY_MAPPING = {'england': 'united_kingdom'}

URL = "https://world-weather.info/forecast/{}/{}/{}-{}/"

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
    # if between 80-85, or between 70-80 and not cloudy
    if (temp > 80) or (temp > 70 and (not 'cloud' in weather.lower())):
        return 'Warm'
    # if between 65-70, or between 70-80 and cloudy
    if temp > 65:
        return 'Mild'
    if temp > 55:
        return 'Chilly'
    if temp > 32:
        return 'Cold'
    return 'Really Cold'


def get_projected_weather(
    city: str, country: str, start_date, end_date
) -> dict:
    """
    Parameters
    ----------
    city : str
    country : str
    start_date : datetime.date
    end_date : datetime.date

    Returns
    -------
    dict 
        Returns dict of lists with keys: ['temps', 'weathers', 'weather_types'].
    """
    weather_info_class_regex = 'ww-month-week(end|days) (fore(a|)cast)(-statistics|)'
    weather_class_regex = 'icon-weather wi d\d{3} tooltip'
    
    date_temps = {}
    temps = []
    weathers = []
    weather_types = []
    for month in range(start_date.month, end_date.month + 1):
        weather_url = URL.format(
            COUNTRY_MAPPING.get(country, country), 
            city.replace(' ', '_'),
            MONTH_MAPPING[month - 1],
            start_date.year,
        )
        print(f'Scraping {weather_url}...')
        soup = BeautifulSoup(requests.get(weather_url).content, 'html.parser')
        sections = soup.find_all(True, {'class': re.compile(weather_info_class_regex)})
        
        # if `BeautifulSoup` doesn't return anything, break out of loop:
        if not sections:
            break

        for x in sections:
            section_date = date(start_date.year, month, int(x.div.text))
            section_temp = int(x.span.text.replace('+', '').replace('°', ''))
            section_weather = x.find(
                True, {'class': re.compile(weather_class_regex)}
            ).get('title')

            if section_date >= start_date and section_date <= end_date:
                date_temps[section_date] = section_temp
                temps.append(section_temp)
                weathers.append(section_weather)
                weather_types.append(get_weather_type(section_temp, section_weather))
            elif section_date > end_date:
                break

    return {
        'temps': temps, 'weathers': weathers, 'weather_types': weather_types
    }
