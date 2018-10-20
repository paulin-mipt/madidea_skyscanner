from flask import Flask, render_template, request, redirect, url_for, jsonify
import json

app = Flask(__name__)


def bad_arguments(cause):
    return 'Sorry, bad city set... Go back and try again, please!\nPossible fault: {}.'.format(cause)


@app.route('/cities', methods=('GET', 'POST'))
def cities():
    with open('static/city_suggest.json') as fin:
    	return jsonify(json.load(fin))


@app.route('/', methods=('GET', 'POST'))
def main():
    if request.method == 'POST':
        cities = []
        for key, values in request.form.lists():
            if key == 'city[]':
                cities = list(values)
        return redirect(url_for('render_map', cities='+'.join(cities)))
    return render_template('index.html')


@app.route('/<path:cities>')
def render_map(cities):
    cities = cities.split('+')
    if len(cities) < 2:
        return bad_arguments('are you travelling alone? You should add more than 1 city')
    return render_template('map.html')


if __name__ == '__main__':
    app.run()
