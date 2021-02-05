import folium

from flask import Flask, request, jsonify, render_template
from haversine import haversine
from folium.plugins import MarkerCluster
from folium.features import DivIcon

from functions import get_coords, price_predict

app = Flask(__name__)

# Static texts
DEFAULT_TEXT = 'Расстояние до Кремля и ориентировочная стоимость аренды:'
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
                cost = price_predict(distance, area, lat, long)

                # Preparing data for the map
                cost_str = ' %s  ₽' % cost
                dist_str = ' %s км' % distance

                start_coords = (lat, long)
                world_map = folium.Map(location=start_coords, zoom_start=16)
                marker_cluster = MarkerCluster().add_to(world_map)
                radius = 10

                # html variables for folium marker
                html_base = '<div style="font-size: 20pt; height: 200px; width: 400px; background:#4CAF50">'
                html_vars = DEFAULT_TEXT+dist_str+' и'+cost_str+'</div>'

                folium.map.Marker([lat, long], icon=DivIcon(
                    icon_size=(150,36),
                    icon_anchor=(0,0),
                    html=html_base+html_vars
                    )).add_to(world_map)
                folium.Marker(location = [lat, long], radius=radius, popup=[DEFAULT_TEXT+dist_str+cost_str], fill =True).add_to(marker_cluster)

                # Result map assemble
                return world_map._repr_html_(), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
