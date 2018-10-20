import requests
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


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


def get_data():
    resp = requests.get('http://partners.api.skyscanner.net/apiservices/geo/v1.0',
                    params={'apiKey': 'ha812346737381611819258748469243'})
    return resp.json()


def fill_geo(path):
    engine = create_engine('sqlite:///' + path, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    data = get_data()
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

if __name__ == '__main__':
    fill_geo('skyscraper.sqlite')
