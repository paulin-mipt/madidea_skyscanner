import requests
import json
from collections import Counter


def get_data(apiKey):
    resp = requests.get('http://partners.api.skyscanner.net/apiservices/geo/v1.0',
                    params={'apiKey': apiKey})
    return resp.json()


def fill_geo(apiKey):
    data = get_data(apiKey)
    countries = {}
    for cont in data['Continents']:
        for country in cont['Countries']:
            countries[country['Id']] = []
            for city in country['Cities']:
                countries[country['Id']].append(city['Name'])
            # session.commit()
    all_cities = []
    for c, cities in countries.items():
        for c in cities:
            all_cities.append(c)
    all_cities = dict(Counter(all_cities))
    dups = []
    for k, v in all_cities.items():
        if v > 1:
            dups.append(k)
    data_for_autosuggest = []
    for cont in data['Continents']:
        for country in cont['Countries']:
            for city in country['Cities']:
                full_name = city['Name']
                if full_name in dups:
                    full_name += ' ({})'.format(country['Id'])
                data_for_autosuggest.append(
                {
                'id': city['Id'],
                'name' : full_name
                }
                )
    return data_for_autosuggest

if __name__ == '__main__':
    with open('apiKey.cred', 'r') as cred:
        apiKey = cred.read()
    data_for_autosuggest = fill_geo(apiKey)
    with open('city_suggest.json', 'w') as file:
        file.write(json.dumps(data_for_autosuggest, indent=4))
