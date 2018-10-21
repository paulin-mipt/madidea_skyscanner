import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, aliased
import os
from collections import defaultdict


def get_flights(cities):
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            'scraper', 'skyscanner.sqlite')
    engine = db.create_engine('sqlite:///' + db_path)
    conn = engine.connect()
    cities = list(map(lambda x: x.lower(), cities))

    query = (
        'select date, price, cityA.name, cityA.id, cityB.name, cityB.id, cityA.lat, cityA.lon, cityB.lat, cityB.lon from quotes as q ' +
        'inner join city as cityA on cityA.id == q."city_A" ' +
        'inner join city as cityB on cityB.id == q."city_B" ' +
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

    result = []
    for city in cities:
        result.append({
            'a_lat' : coordinates[city][0],
            'a_lon' : coordinates[city][1],
            'b_lat' : coordinates[best_city_id][0],
            'b_lon' : coordinates[best_city_id][1],
            'cost' : groups[best_date][best_city_id][city]
        })

    return best_date, names.get(best_city_id), result
