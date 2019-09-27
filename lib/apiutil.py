import os

__name__ = 'dailyforecast'

host = 'https://api.weather.com'

def default_params():
    ########################
    # Read weather credentials
    ########################
    with open('credentials_weather.json', encoding='utf-8') as F:
    #with open('credentials.json', encoding='utf-8') as F:
    #with open('credentials_dev.json', encoding='utf-8') as F:
        credentials = json.loads(F.read())
    return {
        'apiKey': os.environ['WEATHER_API_KEY'],
        'language': 'en-US'
    }

def request_headers():
    return {
        'User-Agent': 'Request-Promise',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip'
    }
