import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, aliased
import os
from collections import defaultdict
from datetime import datetime


def get_skyscanner_url(src, dest, date):
    BASE_URL = 'https://www.skyscanner.ru/transport/flights'
    return '/'.join([BASE_URL, src, dest, ''.join(date.split('-'))[2:]])


def hackupc_flights(cities):
    flights = []

    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           'skyscanner.sqlite')
    print(db_path)
    engine = db.create_engine('sqlite:///' + db_path)
    conn = engine.connect()
    # cities = list(map(lambda x: x.lower(), cities))

    query = (
        'select city.id, city.lat, city.lon from city ' +
        'where city.id in (\"{0}\")'.format(
            '\", \"'.join(cities)
            )
    )
    data = conn.execute(query).fetchall()

    for i in range(len(data)):
        flight = {}
        flight['a_lat'] = data[i][1]
        flight['a_lon'] = data[i][2]
        flight['b_lat'] = 41.383333
        flight['b_lon'] = 2.183333
        flight['cost'] = 'BIENE'
        flight['url'] = 'https://hackupc.com'
        flights.append(flight)
    return '', '', flights


def get_flights(cities, hackupc=False):
    if hackupc:
        return hackupc_flights(cities)

    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           'skyscanner.sqlite')
    engine = db.create_engine('sqlite:///' + db_path)
    conn = engine.connect()
    # cities = list(map(lambda x: x.lower(), cities))

    query = (
        'select date, price, cityA.name, cityA.id, cityB.name, cityB.id, cityA.lat, cityA.lon, cityB.lat, cityB.lon from quotes as q ' +
        'inner join city as cityA on lower(cityA.id) == lower(q."city_A") ' +
        'inner join city as cityB on lower(cityB.id) == lower(q."city_B") ' +
        'where cityA.id in (\"{0}\")'.format(
            '\", \"'.join(cities)
            )
    )
    data = conn.execute(query).fetchall()

    min_price = float('+inf')
    best_date = None
    best_city_id = None

    groups = defaultdict(lambda: defaultdict(dict))
    coordinates = {}
    names = {}
    for date, price, aname, aid, bname, bid, alat, alon, blat, blon in data:
        date = date.split()[0]  # take only date part of datetime string
        groups[date][bid][aid] = float(price)
        coordinates[bid] = (blat, blon)
        coordinates[aid] = (alat, alon)
        names[bid] = bname
        names[aid] = aname

    for date in groups:
        for destination in groups[date]:
            if len(groups[date][destination]) == len(cities):
                price = sum(groups[date][destination].values())
                if price < min_price:
                    min_price = price
                    best_date = date
                    best_city_id = destination

    if best_date is None or best_city_id is None:
        return None, None, []

    # Yup, that is some nasty hack
    best_date_fake = datetime.strftime(
        datetime.strptime(best_date, '%Y-%m-%d')
        - datetime.strptime('2018-10-17', '%Y-%m-%d')
        + datetime.now(), '%Y-%m-%d')

    result = []
    for city in cities:
        result.append({
            'a_lat' : coordinates[city][0],
            'a_lon' : coordinates[city][1],
            'b_lat' : coordinates[best_city_id][0],
            'b_lon' : coordinates[best_city_id][1],
            'cost' : groups[best_date][best_city_id][city],
            'url' : get_skyscanner_url(city, best_city_id, best_date_fake)
        })

    return best_date_fake, names.get(best_city_id), result
