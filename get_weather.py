from datetime import date, timedelta

MONTH_MAPPING = [
    'january', 'feburary', 'march', 
    'april', 'may', 'june', 
    'july', 'august', 'september', 
    'october', 'november', 'december',
]

INFO = {
    'Tel Aviv': ['il', 215854, 215854],
    'Palo Alto': ['us', 94301, 331972],
    'New York': ['us', 10007, 349727],
    'London': ['gb', 'ec4a-2', 328328],
}

URL = "https://www.accuweather.com/en/{}/{}/{}/{}-weather/{}"


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def get_projected_weather(city, start_date, end_date):
    """
    Parameters
    ----------
    city : str
    start_date : datetime.date
    end_date : datetime.date
    """
    city_info = INFO[city]

    for month in range(start_date.month, end_date.month + 1):
            weather_url = URL.format(
                city_info[0], 
                city.lower().replace(' ', '-'), 
                city_info[1], 
                MONTH_MAPPING[month - 1],
                city_info[2],
            )
            print(weather_url)
    # for date in range(start_date, end_date):
