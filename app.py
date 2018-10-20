from flask import Flask, render_template, request, redirect, url_for, jsonify
import json

from trips import get_flights

app = Flask(__name__)


def bad_arguments():
    return 'Sorry, bad city set... Go back and try again, please'


@app.route('/cities', methods=('GET', 'POST'))
def cities():
    with open('static/city_suggest.json') as fin:
    	return jsonify(json.load(fin))

@app.route('/', methods=('GET', 'POST'))
def main():
    if request.method == 'POST':
        cities = []
        if 'city1' in request.form:
            cities.append(request.form['city1'])
        if 'city2' in request.form:
            cities.append(request.form['city2'])
        return redirect(url_for('render_map', cities='+'.join(cities)))
    return render_template('index.html')

@app.route('/<cities>')
def render_map(cities):
    cities = cities.split('+')
    if len(cities) != 2:
        return bad_arguments()
    flights = get_flights(cities)
    return render_template('map.html',
                           flights=flights)

if __name__ == '__main__':
    app.run()
