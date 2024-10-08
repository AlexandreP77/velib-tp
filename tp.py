import requests
from pymongo import MongoClient
import folium
import webbrowser
from geopy.distance import geodesic
def geocode_address(address):
    headers = {
        'User-Agent': 'velib_locator'
    }
    encoded_address = requests.utils.quote(address)
    url = f'https://nominatim.openstreetmap.org/search?q={encoded_address}&format=json&limit=1'
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json():
        location = response.json()[0]
        return float(location['lat']), float(location['lon'])
    else:
        print(" vérifier l'adresse")
        print("URL de la req :", url)
        print("Réponse de l'API:", response.text)
        return None, None
url = 'https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records'
client = MongoClient('mongodb://localhost:27017/')
db = client['velib_db']
collection = db['disponibilite']
user_address = input("Veuillez entrer votre adresse : ")
user_coords = geocode_address(user_address)
if user_coords == (None, None):
    print("Impossible de récupérer les coordonnées de l'adresse")
else:
    print(f"Coordonnées de l'adresse saisie : {user_coords}")
    carte = folium.Map(location=user_coords, zoom_start=13)
    max_distance_km = 2
    for station in collection.find():
        try:
            station_coords = station['coordonnees_geo']
            if isinstance(station_coords, list):
                lat, lon = map(float, station_coords)
            else:
                lat = float(station_coords['lat'])
                lon = float(station_coords['lon'])
            station_name = station['name']
            num_bikes = station['numbikesavailable']
            distance = geodesic(user_coords, (lat, lon)).kilometers
            if distance <= max_distance_km:
                popup_text = f"{station_name} - Vélos disponibles: {num_bikes} - Distance: {round(distance, 2)} km"
                folium.Marker([lat, lon], popup=popup_text).add_to(carte)
        except KeyError:
            print(f"Coordonnées non trouvées pour la station: {station.get('name', 'Inconnue')}")
        except ValueError:
            print(f"Erreur de format de coordonnées pour la station: {station.get('name', 'Inconnue')}")
    carte.save('carte_velib_proximite.html')
    webbrowser.open('carte_velib_proximite.html')