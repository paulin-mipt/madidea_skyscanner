import sqlalchemy as db
from scraper.get_data import City, Country, Quote
from sqlalchemy.orm import sessionmaker, aliased


# flights = [
#         {
#             "a_lat" : 55,
#             "a_lon" : 37,
#             'b_lat' : 30,
#             'b_lon' : 30,
#             'cost' : 300
#         },
#         {
#             'a_lat' : 25,
#             'a_lon' : 17,
#             'b_lat' : 30,
#             'b_lon' : 30,
#             'cost' : 100
#         }
#     ]
def get_flights(cities):
	# right now I fetch 5 random flights
	engine = db.create_engine('sqlite:///scraper/skyscanner.sqlite')
	conn = engine.connect()
	query = (
		'select date, price, cityA.lat, cityA.lon, cityB.lat, cityB.lon from quotes as q ' +
		'inner join city as cityA on cityA.id == q."city_A" ' +
		'inner join city as cityB on cityB.id == q."city_B" ' +
		'where cityA.name in (\"{0}\") and cityB.name in (\"{0}\")'.format(
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