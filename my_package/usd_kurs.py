import requests

def get_usd_to_pln():
    url = "http://api.nbp.pl/api/exchangerates/rates/a/usd/"
    response = requests.get(url)
    data = response.json()
    rate = data['rates'][0]['mid']
    return rate