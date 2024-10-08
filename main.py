import requests
from pymongo import MongoClient

url = 'https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records'

client = MongoClient('mongodb://localhost:27017/')
db = client['velib_db']
collection = db['disponibilite']

map_function = """function() {
    emit(this.station_type, this.numbikesavailable);
}"""

reduce_function = """function(key, values) {
    return Array.sum(values);
}"""

limit = 100  
offset = 0
total_records_inserted = 0

while True:
    params = {'limit': limit, 'offset': offset}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()

        if data and 'results' in data and data['results']:
            collection.insert_many(data['results'])
            total_records_inserted += len(data['results'])
            print(f"{len(data['results'])} enregistrements ajoutés à MongoDB avec succès.")

            offset += limit
        else:
            print("Toutes les données ont été récupérées ou aucun enregistrement n'a été trouvé.")
            break
    else:
        print(f"Erreur lors de la requête : {response.status_code}")
        break

result = collection.map_reduce(map_function, reduce_function, "velib_summary")

print("Résultats de MapReduce :")
for doc in result.find():
    print(doc)

print(f"Nombre total d'enregistrements ajoutés à MongoDB : {total_records_inserted}")
