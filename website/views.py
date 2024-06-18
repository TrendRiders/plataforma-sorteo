from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from .models import Note
from . import db
import pandas as pd
import json
from . import db_mongo   ##means from __init__.py import db

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user, sorteos = get_ids())


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


@views.route('/uploader', methods=['POST'])
@login_required
def upload_file():
    result_sorteados = []
    cant_doc = None

    if request.method == 'POST':
        f = request.files['file']
        f.save(f.filename)
        print('ARCHIVO',f.filename)
        fecha_inicio = datetime.strptime(request.form['init_date'],'%Y-%m-%d')
        fecha_fin = datetime.strptime(request.form['end_date'],'%Y-%m-%d')

        num_sorteados = int(request.form['num_sorteados'])
        id_sorteo = str(request.form['nom_sorteo'])

        df = pd.read_csv(f.filename)
        sorteados = {}

        df['hora1'] = pd.to_datetime(df['hora'], format='%Y-%m-%dT%H:%M:%S.%fZ')

        #filtrar por fecha

        df_filtrado = df[(df['hora1'] >= fecha_inicio) & (df['hora1'] < fecha_fin)]

        
        while len(sorteados) < num_sorteados:
            registro = df_filtrado.sample()
            _id = registro.values[0][0]  
            nombre = registro.values[0][1] 
            numero = registro.values[0][2] 
            sorteados[numero] = {'nombre': nombre, 'id_participacion': _id}


        df_sorteados = pd.DataFrame(columns=df.columns)  

        count = 1
        for numero, reg in sorteados.items():

            result_sorteados.append({'Numero': count, 'Nombre': reg['nombre'], 'ID_Participacion': reg['id_participacion']})
            count +=1
            df_sorteados = df_sorteados._append(df_filtrado[df_filtrado['ID'] == reg['id_participacion']] )  # Agregar el registro correspondiente a df_sorteados


        df_sorteados.to_csv('aux_file.csv', index=False)
        
        sorteos = None

        cant_doc = get_size_bd()

        guardar_sorteo_bd('aux_file.csv', id_sorteo)

        print(result_sorteados)
        
    return render_template("home.html", user=current_user, sorteos=get_ids(), sorteados = result_sorteados)


def get_size_bd():
    collection = db_mongo['sorteos']
    ids = [str(document['_id']) for document in collection.find({}, {'_id': 1})]
    return len(ids)

def get_ids():
    collection = db_mongo['sorteos']
    ids = [str(document['_id']) for document in collection.find({}, {'_id': 1})]
    return ids

def guardar_sorteo_bd(csv_file, id):

    df = pd.read_csv(csv_file)
    collection = db_mongo['sorteos']
    csv_dict = df.to_dict(orient='list')
    csv_dict['_id'] = str(id)
    collection.insert_one(csv_dict)
    return 


@views.route('/display_sorteo', methods=['POST'])
@login_required
def handle_button_click():
    sorteados = []
    cant_doc = None

    if request.method == 'POST':
        button_index = request.form.get('button_index')
        collection = db_mongo['sorteos']

        # Consultar un documento en MongoDB
        document = collection.find_one({"_id": str(button_index)})  # Reemplaza "valor_del_id" con el ID del documento que deseas recuperar

        # Crear un DataFrame en pandas
        df = pd.DataFrame(document)

        # Mostrar el DataFrame
        print(df)
        sorteados = []

        count = 1
        cant_doc = get_size_bd()

        for indice, fila in df.iterrows():
            sorteados.append({'Numero': count, 'Nombre': fila['Name'], 'ID_Participacion': fila['ID']})
            count+=1
        print(sorteados)

    return sorteados

#{'Numero': 1, 'Nombre': 'Andrew Thomas', 'ID_Participacion': '51919537684_1'},




@views.route('/borrar-sorteo', methods=['POST'])
@login_required
def borrar_sorteo():
    button_index = request.form.get('button_index')

    collection = db_mongo['sorteos']
    result = collection.delete_one({'_id': button_index})  # Borra el documento con el _id especificado
    
    return jsonify({'message': 'Sorteo borrado correctamente'})
    
