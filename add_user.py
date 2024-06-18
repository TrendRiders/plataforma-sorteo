from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

client = MongoClient('mongodb://Molitalia:kg6Ui75GhtdHTESy45ygKUgo78IghTY54s@34.125.134.86:27017/?authSource=admin')
db_mongo = client['moli-codigos']
collection = db_mongo['users_dash']


usuario = 'admin'
contrasena = 'admin'



documento = {
    '_id' : usuario,
    'password' : contrasena
}



resultado = collection.insert_one(documento)
