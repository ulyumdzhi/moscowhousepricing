import requests
import joblib
import folium

from sklearn.ensemble import GradientBoostingRegressor

YANDEX = '301d8157-1143-4ec9-95aa-73d51f27bdb8'

clf = joblib.load('regressor.joblib')

def get_coords(address):

    geodata = requests.get(
    f'https://geocode-maps.yandex.ru/1.x/?apikey={YANDEX}&geocode={address}&format=json'
    ).json()

    lat, lon = geodata['response'][
    'GeoObjectCollection'][
    'featureMember'][0][
    'GeoObject'][
    'Point'][
    'pos'].split()

    area_name = geodata['response'][
    'GeoObjectCollection'][
    'featureMember'][0][
    'GeoObject'][
    'metaDataProperty'][
    'GeocoderMetaData'][
    'AddressDetails'][
    'Country'][
    'AdministrativeArea'][
    'AdministrativeAreaName']

    return float(lat), float(lon), area_name

def price_predict(distance, area, lat, long):

    data = [[distance, area, lat, long]]
    pred = clf.predict(data)
    cost = round(pred[0])

    return cost
