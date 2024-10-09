import requests
from pymongo import MongoClient

# URL de l'API des disponibilités Vélib' en temps réel
url = 'https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records'

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['velib_db']
collection = db['disponibilite']

# Paramètres pour la pagination de l'API
limit = 100  
offset = 0
total_records_inserted = 0

# Boucle pour récupérer les données par pagination
while True:
    params = {'limit': limit, 'offset': offset}
    response = requests.get(url, params=params)
    
    # Vérification du code de statut de la réponse
    if response.status_code == 200:
        data = response.json()

        # Vérification de la présence de données à insérer
        if data and 'records' in data and data['records']:
            # Insertion des données dans MongoDB
            collection.insert_many(data['records'])
            total_records_inserted += len(data['records'])
            print(f"{len(data['records'])} enregistrements ajoutés à MongoDB avec succès.")

            # Mise à jour de l'offset pour la prochaine requête
            offset += limit
        else:
            print("Toutes les données ont été récupérées ou aucun enregistrement n'a été trouvé.")
            break
    else:
        print(f"Erreur lors de la requête : {response.status_code}")
        break

# Affichage du nombre total d'enregistrements ajoutés
print(f"Nombre total d'enregistrements ajoutés à MongoDB : {total_records_inserted}")


