from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from . import db_mongo   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        collection = db_mongo['users_dash']


        user = request.form.get('user')
        valid_user = collection.find_one({'_id': user})
        password = request.form.get('password')

        if valid_user:
            passw = generate_password_hash(password, method='pbkdf2:sha256')
            print(passw)

            if valid_user['password'] == password:
                flash('Logged in successfully!', category='success')
                usuario = User(id=user, password=passw)
                login_user(usuario, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    
    cant_doc = get_size_bd()
    return render_template("login.html", user=current_user, sorteos=cant_doc)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


def get_size_bd():
    collection = db_mongo['sorteos']
    ids = [str(document['_id']) for document in collection.find({}, {'_id': 1})]
    return len(ids)