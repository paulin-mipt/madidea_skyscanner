import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, aliased
import os


def get_flights(cities):
	# right now I fetch 5 random flights
	db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                        	'scraper', 'skyscanner.sqlite')
	engine = db.create_engine('sqlite:///' + db_path)
	conn = engine.connect()
	query = (
		'select date, price, cityA.lat, cityA.lon, cityB.lat, cityB.lon from quotes as q ' +
		'inner join city as cityA on cityA.id == q."city_A" ' +
		'inner join city as cityB on cityB.id == q."city_B" ' +
		'where cityA.name in (\"{0}\") or cityB.name in (\"{0}\")'.format(
			'\", \"'.join(cities)
			)
	)
	print(query)
	data = conn.execute(query).fetchall()
	result = [
	{
		'a_lat' : alat,
		'a_lon' : alon,
		'b_lat' : blat,
		'b_lon' : blon,
		'cost' : price
	} for date, price, alat, alon, blat, blon in data
	]
	return result