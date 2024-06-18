from flask import Flask, request, jsonify, send_from_directory
import requests
import json
import time
import os
import http.client
import ssl
from pymongo import MongoClient
from bson.objectid import ObjectId  # Importa ObjectId
from http.server import BaseHTTPRequestHandler, HTTPServer

IMAGES_DIR = 'images'

app = Flask(__name__)

#MONGO CREDENTIALS
mongo_user = 'Molitalia'
mongo_pwd = 'kg6Ui75GhtdHTESy45ygKUgo78IghTY54s'
server_ip = '34.125.134.86:27017'
auth_db = 'admin'
client = MongoClient('mongodb://{}:{}@{}/?authSource={}'.format(mongo_user,mongo_pwd,server_ip,auth_db))
db = client['moli-codigos']  



@app.route('/checkuser/<numero>', methods=['GET'])
def check_user(numero):
    collection = db['usuarios']
    resultado = collection.find_one({'_id': numero})

    if resultado:
        print('usuario existente')
        return jsonify(resultado), 200
    else:
        return jsonify({}), 404


@app.route('/checkcode/<codigo>', methods=['GET'])

def check_code(codigo):
    collection = db['codigos_db']
    resultado = collection.find_one({'_id': codigo})
    
    resultado['_id'] = str(resultado['_id'])

    if resultado:
        return jsonify(resultado), 200
    else:
        return jsonify({'codigo':''}),404


@app.route('/registeruser/<numero>/<dni>/<nombre>', methods=['POST'])
def register_user(numero,dni,nombre):

    collection = db['usuarios']
    documento = {
        '_id': numero,  # Especifica el valor de _id que desees
        'dni': dni,
        'nombre': nombre,
        'participaciones' : 0
        # Añade más campos según necesites
    }

    try:
        resultado = collection.insert_one(documento)
        print(f"Documento insertado con el _id: {resultado.inserted_id}")
        return jsonify({}),201
    except Exception as e:
        print(f"Error al insertar el documento: {e}")
        return jsonify({'msj':'error al insertar'}),204


@app.route('/set_participaciones/<numero>/<participaciones>', methods=['PATCH'])
def set_participaciones(numero,participaciones):
    collection = db['usuarios']
        
    cambios = {
            '$set': {
                'participaciones': int(participaciones)
            }
        }
    resultado = collection.find_one_and_update(
        {'_id': numero}, # Usa ObjectId para convertir el string a un objeto ObjectId
        cambios,
        return_document=True # Retorna el documento después de la actualización
    )

    if resultado:
        print("Status participaciones actualizado:", resultado)
        return jsonify({'msj':'part actualizadas'})
    else:
        print("No se encontró el usuario para actualizar participaciones.")
        return jsonify({'msj':'no se pudo actualizar'})


@app.route('/update_codigo/', methods=['PATCH'])
def update_codigo():
    data = request.json
    numero = data['numero']
    codigo = data['codigo']
    link = data['link']
    collection = db['codigos_db']
        
    cambios = {
            '$set': {
                'link': link,
                'user' : numero
            }
        }
    resultado = collection.find_one_and_update(
        {'_id': codigo}, # Usa ObjectId para convertir el string a un objeto ObjectId
        cambios,
        return_document=True # Retorna el documento después de la actualización
    )

    if resultado:
        print("Status codigo actualizado:", resultado)
        return jsonify({'msj':'codigo actualizado'})
    else:
        print("No se encontro codigo.")
        return jsonify({'msj':'codigo no actualizado'})




@app.route('/images/<filename>')
def serve_image(filename):
    # Asegúrate de que el nombre del archivo termine en .jpg
    if not filename.endswith('.jpg'):
        abort(404)  # No encontrado

    # Sirve el archivo de la carpeta 'imagenes', si existe
    if os.path.isfile(os.path.join(IMAGES_DIR, filename)):
        return send_from_directory(IMAGES_DIR, filename)
    else:
        abort(404)  # No encontrado


@app.route('/upload', methods=['POST'])
def upload():
    # Obtiene el link de la imagen del body del request
    data = request.json
    
    #print(data)

    photo_url = data['image_url']['url']
    id_participation = data['id']


    print('URL de la foto:', photo_url)
    print('Participacion:', id_participation)


    save_path = os.path.join(os.path.dirname(__file__), 'images')
    os.makedirs(save_path, exist_ok=True)

    conn = http.client.HTTPSConnection("ppv8re.api.infobip.com")
    payload = ''
    headers = {
        'Authorization': 'App fcc0b4a83f37b89a5b1b2f97a4193d80-19ac63c9-b3a0-47d3-8764-04b91be9ceed',
        'Accept': 'application/json'
    }

    start_pos = photo_url.find("/whatsapp/")

    extracted_path = photo_url[start_pos:]

    conn.request("GET", extracted_path, payload, headers)
    res = conn.getresponse()
    data = res.read()
    image_filename = os.path.join(save_path, '{}.jpg'.format(id_participation))
    image_path = os.path.join(os.getcwd(), image_filename)  # Asegúrate de usar la extensión correcta

        # Guardar la imagen en el directorio del programa
    with open(image_filename, 'wb') as file:
        file.write(data)


    print('Imagen guardada en:', image_filename)

    # Genera la URL pública del servidor
    public_ip = '34.125.11.181'
    public_url = 'http://{}:{}/images/{}.jpg'.format(public_ip, "8000", id_participation)

    print('URL pública:', public_url)

   

    response = {"link": public_url}
    return jsonify(response), 200



@app.route('/queue', methods=['POST'])
def handle_post():
    if request.method == 'POST':

        #PROCESAR DATA REQUEST
        data = request.json
        numero = data['numero']
        

        #ENTRAR COLA
        collection = db['queue']
        resultado = collection.insert_one({"numero": numero})
        id_queue = None
        if resultado:
            id_queue = resultado.inserted_id
            print("Ingresado a la cola")
        else:
            print("No se pudo entrar a la cola.")


        #BUSCAR SI ERES PRIMERO
        collection = db['queue']
        resultado = collection.find_one({}, sort=[('_id', 1)])  # Nota el argumento sort como una lista de tuplas

        if resultado:
            num = resultado['numero']
            while num != numero:
                print('Esperó 2s')
                time.sleep(2)
                resultado = collection.find_one({}, sort=[('_id', 1)])  # Nota el argumento sort como una lista de tuplas
                num = resultado['numero']
            print("Es tu turno")
        else:
            print("Error leyendo turno de cola")



        #BUSCAR CODIGO
        collection = db['aux_codigos']

        resultado = collection.find_one({'user': ''})
        codigo = None

        if resultado:
            codigo = resultado['_id']
            print("Codigo obtenido:")
        else:
            print("Error buscando codigo")



        #UPDATE DE CODIGO
        cambios = {
            '$set': {
                'user': numero
            }
        }
        resultado = collection.find_one_and_update(
            {'_id': codigo}, # Usa ObjectId para convertir el string a un objeto ObjectId
            cambios,
            return_document=True # Retorna el documento después de la actualización
        )

        if resultado:
            print("Status codigo actualizado:", resultado)
        else:
            print("No se encontró el codigo para actualizar status.")


        #QUITARSE DE LA COLA
        collection = db['queue']

        resultado = collection.delete_one({'_id': ObjectId(id_queue)})

        # Verifica si el documento fue eliminado
        if resultado.deleted_count > 0:
            print(f"Documento con _id eliminado exitosamente.")
        else:
            print(f"No se encontró el documento con _id  para eliminar.")


        response = {"codigo": codigo}
        return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

