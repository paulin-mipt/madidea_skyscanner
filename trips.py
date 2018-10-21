import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, aliased
import os
from collections import defaultdict


def get_flights(cities):
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            'scraper', 'skyscanner.sqlite')
    engine = db.create_engine('sqlite:///' + db_path)
    conn = engine.connect()
    query = (
        'select date, price, cityA.name, cityB.name, cityA.lat, cityA.lon, cityB.lat, cityB.lon from quotes as q ' +
        'inner join city as cityA on cityA.id == q."city_A" ' +
        'inner join city as cityB on cityB.id == q."city_B" ' +
        'where cityA.name in (\"{0}\")'.format(
            '\", \"'.join(cities)
            )
    )
    data = conn.execute(query).fetchall()

    min_price = float('+inf')
    best_date = None
    best_city = None

    groups = defaultdict(lambda: defaultdict(dict))
    coordinates = {}
    for date, price, aname, bname, alat, alon, blat, blon in data:
        date = date.split()[0]  # take only date part of datetime string
        groups[date][bname][aname] = float(price)
        coordinates[bname] = (blat, blon)
        coordinates[aname] = (alat, alon)

    for date in groups:
        for destination in groups[date]:
            if len(groups[date][destination]) == len(cities):
                price = sum(groups[date][destination].values())
                if price < min_price:
                    min_price = price
                    best_date = date
                    best_city = destination


    if best_date is None or best_city is None:
        return None, None, []

    result = []
    for city in cities:
        result.append({
            'a_lat' : coordinates[city][0],
            'a_lon' : coordinates[city][1],
            'b_lat' : coordinates[best_city][0],
            'b_lon' : coordinates[best_city][1],
            'cost' : groups[best_date][best_city][city]
        })

    return best_date, best_city, result
