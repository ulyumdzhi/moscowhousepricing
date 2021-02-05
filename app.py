from flask import Flask, request, jsonify, render_template, url_for
import folium
import math
import requests
import joblib

from haversine import haversine
from sklearn.ensemble import GradientBoostingRegressor

from functions import get_coords, moscow_price

app = Flask(__name__)

# Static texts
HEADER_INIT_TEXT = 'Хэллоу, бой! Давай узнаем сколько стоит снять твою берлогу!'
HEADER_TEXT_2CLOSE = 'Уоуоу, бой! Подальше от Кремля, плиз!'
HEADER_TEXT_FARFARAWAY = 'оуоуоуоуоуоуоу, бой! Адрес московский укажи, плиз!'
NOT_MOSCOW = 'Адрес не в Москве!'
TOO_CLOSE = 'Слишком близко к Кремлю! Тсссс!'

# Moscow Kremlin coordinates
KREMLIN_LAT = 55.75141
KREMLIN_LONG = 37.61896

@app.route('/', methods=['GET', 'POST'])
def route_price():

    if request.method == 'GET':
        return render_template('index.html', header=HEADER_INIT_TEXT), 200

    if request.method == 'POST':
        # Input data processing
        area = float(request.form['area'])
        input_address = str(request.form['address'])
        long, lat, region = get_coords('Москва, '+input_address)

        # Check for Moscow address
        if region != 'Москва':
            print(NOT_MOSCOW)
            not_moscow = 'Москва (а не %s!), ' %region
            return render_template('index.html', header=HEADER_TEXT_FARFARAWAY, not_mos=not_moscow), 200

        else:
            # Distance between address and Moscow city center (km)
            distance = round(haversine((lat, long), (KREMLIN_LAT, KREMLIN_LONG)))
            AROUND_KREMLIN = 0.51     # Nobody can live at Kremlin except President

            # If too close
            if distance < AROUND_KREMLIN:
                print(TOO_CLOSE)
                return render_template('index.html', header=HEADER_TEXT_2CLOSE), 200

            # Resulting map
            else:
                return moscow_price(distance, area, lat, long)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
