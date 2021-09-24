import re
import requests 

from bs4 import BeautifulSoup
from datetime import date, timedelta

MONTH_MAPPING = [
    'january', 'feburary', 'march', 
    'april', 'may', 'june', 
    'july', 'august', 'september', 
    'october', 'november', 'december',
]

COUNTRY_MAPPING = {'england': 'united_kingdom'}

URL = "https://world-weather.info/forecast/{}/{}/{}-{}/"


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def get_weather_type(temp, weather):
    if 'rain' in weather.lower():
        return 'Rainy'

    if temp < 50:
        return 'Cold'
    if temp < 60:
        return 'Chilly'
    if temp < 70:
        return 'Mild'
    if temp < 80:
        if 'cloud' in weather.lower():
            return 'Mild'
        return 'Warm'
    if temp < 85:
        return 'Warm'
    return 'Hot' 
    

def get_projected_weather(city, country, start_date, end_date):
    """
    Parameters
    ----------
    city : str
    start_date : datetime.date
    end_date : datetime.date
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

    return temps, weathers, weather_types
