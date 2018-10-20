import requests
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
import datetime 
import tqdm


n_days = 30
today = datetime.datetime.today()

Base = declarative_base()

class Country(Base):
    __tablename__ = 'country'
    id = Column(String, primary_key=True)
    name = Column(String)
    currency = Column(String)

    def __init__(self, id, name, currency):
        self.id = id
        self.name = name
        self.currency = currency

    def __repr__(self):
        return "<Country('%s','%s', '%s')>" % (self.id, self.name, self.currency)


class City(Base):
    __tablename__ = 'city'
    id = Column(String, primary_key=True)
    name = Column(String)
    code = Column(String)
    country_id = Column(String)
    lat = Column(Float)
    lon = Column(Float)

    def __init__(self, id, name, code, country_id, lat, lon):
        self.id = id
        self.name = name
        self.code = code
        self.country_id = country_id
        self.lat = lat
        self.lon = lon

    def __repr__(self):
        return "<City('%s','%s', '%s')>" % (self.name, self.lat, self.lon)


class Quote(Base):
    __tablename__ = 'quotes'
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
        return "<Quote('%s','%s', '%s', '%s')>" % (self.id, self.city_A, self.city_B, self.date)


def get_cities_data(apiKey):
    resp = requests.get('http://partners.api.skyscanner.net/apiservices/geo/v1.0',
                    params={'apiKey': apiKey})
    return resp.json()


def fill_geo(apiKey, session):
    data = get_cities_data(apiKey)
    for cont in data['Continents']:
        print(cont['Name'], cont['Id'])
        for country in cont['Countries']:
            print(country['Name'])
            cntry = Country(country['Id'], country['Name'], country['CurrencyId'])
            session.add(cntry)
            for city in country['Cities']:
                loc = city['Location']
                lat = float(loc.split(',')[1].strip())
                lon = float(loc.split(',')[0].strip())
                cty = City(city['Id'], city['Name'], city['IataCode'], city['CountryId'], lat, lon)
                session.add(cty)
            session.commit()


def get_quotes(A, B, date, apiKey, locale='en-GG', country='ES', currency='EUR'):
    req = ['http://partners.api.skyscanner.net/apiservices/browsequotes/v1.0',
           country,
           currency,
           locale,
           A, B, date
    ]
    req = '/'.join(req)
    print(req)
    resp = requests.get(req,
                       params={'apiKey': apiKey})
    return resp


def process_quotes(data):
    places = {}
    for place in data['Places']:
        if 'CityId' in place:
            places[place['PlaceId']] = {'CityId': place['CityId'].lower()}
    for quote in data['Quotes']:
        yield (
            places[quote['OutboundLeg']['OriginId']]['CityId'],
            places[quote['OutboundLeg']['DestinationId']]['CityId'],
            quote['MinPrice']
        )


def fill_quotes_graph(apiKey, session):
    all_cities = session.query(City).all()
    for date in [today + datetime.timedelta(days=x) for x in range(1, n_days)]:
        print(date.strftime("%Y%m%d"))
        for cityA in tqdm.tqdm(all_cities):
            quotes = get_quotes(cityA.id, 'anywhere', date.strftime("%Y-%m-%d"), 'ha812346737381611819258748469243')
            data = quotes.json()
            if 'Quotes' in data and len(data['Quotes']) == 0:
                continue
            else:
                print(cityA)
            for a, b, price in process_quotes(data):
                quote = Quote(a, b, date, price)
                session.add(quote)
            session.commit()     


def fill_data(path, apiKey):
    engine = create_engine('sqlite:///' + path, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    fill_geo(apiKey, session)
    fill_quotes_graph(apiKey, session)


if __name__ == '__main__':
    with open('apiKey.cred', 'r') as cred:
        apiKey = cred.read()
    fill_data('skyscanner1.sqlite', apiKey)