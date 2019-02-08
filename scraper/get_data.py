import requests
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
import datetime 
import tqdm
import sys


n_days = 30
today = datetime.datetime.today()

Base = declarative_base()


class City(Base):
    __tablename__ = 'city'
    id = Column(String, primary_key=True)
    name = Column(String)
    country_id = Column(String)
    lat = Column(Float)
    lon = Column(Float)

    def __init__(self, id, name, country_id, lat, lon):
        self.id = id
        self.name = name
        self.country_id = country_id
        self.lat = lat
        self.lon = lon

    def __repr__(self):
        return "<City('%s','%s', '%s')>" % (self.name, self.lat, self.lon)


class Route(Base):
    __tablename__ = 'routes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    city_A = Column(String)
    city_B = Column(String)
    date = Column(DateTime)
    price = Column(String)
    url = Column(String)

    def __init__(self, city_A, city_B, date, price, url=None):
        self.city_A = city_A
        self.city_B = city_B
        self.date = date
        self.price = price
        self.url = url

    def __repr__(self):
        return "<Route('%s','%s', '%s', '%s')>" % (self.id, self.city_A, self.city_B, self.date)


def fill_geo_from_file(path, session):
    with open(path) as json_data:
        data = json.load(json_data)
    # {"time_zone":"America/Denver","name":"Santa Fe","coordinates":{"lon":120.43236,"lat":30.236935},"code":"ZSH","country_code":"US"}
    for city in data:
        try:
            obj = City(
                city['code'],
                city['name'],
                city['country_code'],
                city['coordinates']['lat'],
                city['coordinates']['lon'])
            session.add(obj)
        except Exception as e:
            print(city, e)
    session.commit()


def get_routes(A, B, date, apiKey, currency='EUR'):
    resp = requests.get('http://api.travelpayouts.com/v2/prices/month-matrix', params={
        'month': date,
        'origin': A,
        'destination': B,
        # 'currency': currency,
        'token': apiKey
    })#, config={'verbose': sys.stderr})
    return resp

# {'number_of_changes': 0, 'found_at': '2019-02-08T18:29:55', 'distance': 1938, 'duration': 170, 'actual': True, 
#  'value': 8748.0, 'gate': 'OneTwoTrip', 'show_to_affiliates': True, 'origin': 'MOW', 'return_date': None, 
#  'trip_class': 0, 'depart_date': '2019-02-10', 'destination': 'SLY'}
def parse_routes(data):
    for route in data:
        yield route['origin'], route['destination'], route['depart_date'], route['value']


def fill_routes(apiKey, session):
    always_present_city = 'MOW'
    all_cities = session.query(City).all()
    valid_cities = set()
    for city in tqdm.tqdm(all_cities):
        routes = get_routes(always_present_city, city.id, '2019-02-01', apiKey)
        if routes.status_code == 200:
            print(city.id)
            valid_cities.add(city)
            data = routes.json()['data']
            if len(data) > 0:
                for a, b, date, price in parse_routes(data):
                    route = Route(a, b, datetime.datetime.strptime(date, '%Y-%m-%d'), price)
                    session.add(route)
                session.commit()     
    print(len(valid_cities))


def fill_data(path, apiKey):
    engine = create_engine('sqlite:///' + path, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    fill_geo_from_file('./static/cities.json', session)
    fill_routes(apiKey, session)


if __name__ == '__main__':
    with open('apiKey.cred', 'r') as cred:
        apiKey = cred.read()
    fill_data('aviasales1.sqlite', apiKey)