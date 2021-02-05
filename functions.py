import folium
import math
import requests
import joblib

from sklearn.ensemble import GradientBoostingRegressor
from folium.plugins import MarkerCluster
from folium.features import DivIcon

YANDEX = 'your_yandex_api_key'

DEFAULT_TEXT = 'Расстояние до Кремля и ориентировочная стоимость аренды:'

clf = joblib.load('regressor.joblib')

def get_coords(address):

    geodata = requests.get(
    f'https://geocode-maps.yandex.ru/1.x/?apikey={YANDEX}&geocode={address}&format=json'
    ).json()

    lat, lon = geodata[
    'response'
    ][
    'GeoObjectCollection'
    ][
    'featureMember'
    ][0][
    'GeoObject'
    ][
    'Point'
    ][
    'pos'
    ].split()

    area_name = geodata['response']['GeoObjectCollection']['featureMember'][0][
    'GeoObject'
    ].get(
    'metaDataProperty'
    ).get(
    'GeocoderMetaData'
    ).get(
    'AddressDetails'
    ).get(
    'Country'
    ).get(
    'AdministrativeArea'
    ).get(
    'AdministrativeAreaName'
    )
    return float(lat), float(lon), area_name

def moscow_price(distance, area, lat, long):

    data = [[distance, area, lat, long]]
    pred = clf.predict(data)
    cost = round(pred[0])

    cost_str = ' %s  ₽' % cost
    dist_str = ' %s км' % distance

    start_coords = (lat, long)
    world_map = folium.Map(location=start_coords, zoom_start=16)
    marker_cluster = MarkerCluster().add_to(world_map)
    radius = 10

    html_base = '<div style="font-size: 20pt; height: 200px; width: 400px; background:#4CAF50">'
    html_vars = DEFAULT_TEXT+dist_str+' и'+cost_str+'</div>'

    folium.map.Marker([lat, long], icon=DivIcon(
        icon_size=(150,36),
        icon_anchor=(0,0),
        html=html_base+html_vars
        )
    ).add_to(world_map)

    folium.Marker(location = [lat, long], radius=radius, popup=[DEFAULT_TEXT+dist_str+cost_str], fill =True).add_to(marker_cluster)

    return world_map._repr_html_(), 200
