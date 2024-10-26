from flask import Flask, render_template, request, redirect, url_for, flash
from random import randint
from flask_login import LoginManager, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

# IMPORT PER GESTIRE GLI UTENTI
from models import User

# IMPORT PER GESTIRE SERVIZI
import QOS

# IMPORT PER GESTIRE LA BASE DI DATI
import db_interactions
import comments_db_interactions
import post_db_interactions

# IMPORT PER GESTIRE LE DATE
import datetime

LETTURA = 'r'
DEFAULT_USR = 'Anonimo92'
DEFAULT_USR_PP = 'img/generic.jpg'

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'Giacomino si è fatto la bua stamattina'

utente = {'logged': False, 'username': ''}


@app.context_processor
def inject_today_date():
    return {'today_date': datetime.date.today()}


posts = post_db_interactions.fetch_posts()


@app.route('/nuovo_post/', methods=['POST'])
@login_required
def nuovo_post():
    if request.method == 'POST':
        numpost = len(posts)
        nuovo = request.form.to_dict()

        nuovo['username'] = utente['username']

        if len(nuovo['text']) < 30 or len(nuovo['text']) > 200:
            app.logger.error('Lunghezza del post non valida')
            return redirect(url_for('home_page'))
        if str(nuovo['date']) > str(inject_today_date()['today_date']):
            app.logger.error('Peschi nel futuro?')
            return redirect(url_for('home_page'))

        try:
            if str(request.files.to_dict()['image']):
                float(nuovo['weight']) + float(nuovo['length'])
            if not 0.10 < float(nuovo['weight']) < 120 or not 5 < float(nuovo['length']) < 300:
                raise ValueError
        except ValueError:
            app.logger.error('Formati invalidi')
            return redirect(url_for('home_page'))
        except TypeError:
            app.logger.error('Formati invalidi')
            return redirect(url_for('home_page'))

        nuovo["profile"] = db_interactions.get_usr_image(nuovo['username'])
        nuovo['image'] = str(request.files.to_dict()['image'])

        if not nuovo["image"]:
            foto = '*'
        else:
            foto = nuovo['image']

        if foto != '*' and str(str(str(foto).split('/')[1]).split("\'")[0]) not in "jpeg jpg png heif":
            app.logger.error('Non una foto')
            return redirect(url_for('home_page'))
        elif foto != '*':
            nuovo['image'] = 'img/pesci/' + str(foto).split("\'")[1]

        if foto != '*':
            data = nuovo["date"].split('-')
        else:
            data = str(inject_today_date()['today_date']).split('-')

        date = ""
        for i in range(len(data)-1, -1, -1):
            date = date+data[i] + '-'

        nuovo["date"] = date[0:len(date)-1:1]
        nuovo["likes"] = randint(0, 10)

        if foto != '*':
            nuovo["type"] = "<b>" + str(str(str(str(foto).split('/')[0]).split("\'")[1]).split('.')[0]).upper() + "</b>"
        else:
            nuovo["type"] = "*"

        if nuovo["type"] != '*' and not (3 < len(nuovo['location']) < 40):
            app.logger.error('Che posto è?')
            return redirect(url_for('home_page'))


        posts.append(nuovo)

        post_db_interactions.inserisci_nuovo_post(nuovo)

        return render_template("Home.html", lista_post=posts, numpost=len(posts), user=utente)
    else:
        return redirect(url_for('home_page'))


@app.route('/')
def home_page():
    return render_template("Home.html", lista_post=posts, numpost=len(posts), user=utente)


@app.route('/post/<int:id>')
def postato(id):
    commenti = comments_db_interactions.fetch_commenti(id-1)

    return render_template("post.html", post=posts[id-1], commenti_post=commenti, numcommenti=len(commenti), id=id-1, user=utente)


@app.route('/Chi_Siamo.html')
def chi_siamo():
    immagini = db_interactions.fetch_chi_siamo_image()

    return render_template("Chi_Siamo.html", immagine=immagini[randint(0, len(immagini)-1)], user=utente)


@app.route('/post/<int:id>', methods=['POST'])
def new_commento(id):

    if request.method == 'POST':
        nuovo = request.form.to_dict()

        try:
            if nuovo['anonimo'] == 'on':
                nuovo['username'] = DEFAULT_USR
            x = 'e'
        except KeyError:
            x = nuovo['username'][0]
            nuovo['username'] = nuovo['username'][1::]
            if not comments_db_interactions.check_user(nuovo['username']):
                app.logger.error('utente non presente')
                return redirect(url_for('postato', id=id, user=utente))

        if not utente['logged'] and nuovo['username'] != DEFAULT_USR:
            return redirect(url_for('postato', id=id, user=utente))

        if utente['logged'] and utente['username'] != nuovo['username'] and nuovo['username'] != DEFAULT_USR:
            return redirect(url_for('postato', id=id, user=utente))

        if nuovo['username'] != DEFAULT_USR and ((not 3 < len(nuovo['username']) < 30) or x != '@'):
            app.logger.error('username non valido')
            return redirect(url_for('postato', id=id, user=utente))

        if len(nuovo['text']) < 5 or len(nuovo['text']) > 200:
            app.logger.error('Lunghezza del commento non valida')
            return redirect(url_for('postato', id=id, user=utente))

        nuovo['date'] = '-'.join((str(inject_today_date()['today_date']).split('-'))[::-1])

        nuovo['image'] = request.files.to_dict()['image']

        try:
            nuovo['image'].split('/')
            foto = nuovo['image']
        except AttributeError:
            foto = '*'

        if foto != '*' and str(foto).split("'")[1].split('.')[1] not in "jpeg jpg png heif":
            app.logger.error('Non una foto')
            return redirect(url_for('postato', id=id, user=utente))

        if foto != '*':
            nuovo["image"] = "img/risposte/" + str(foto).split("'")[1]

        nuovo["image"] = foto
        nuovo["likes"] = randint(0, 10)

        if nuovo['username'] == DEFAULT_USR:
            nuovo['profile'] = DEFAULT_USR_PP
        else:

            data = str(inject_today_date()['today_date']).split('-')

            date = ""
            for i in range(len(data) - 1, -1, -1):
                date = date + data[i] + '-'

            nuovo["date"] = date[0:len(date) - 1:1]

        comments_db_interactions.add_comment(nuovo, id, DEFAULT_USR)

    return redirect(url_for('postato', id=id, user=utente))


@app.route('/login')
def login_page():
    return render_template('Login.html', user=utente)


@login_manager.user_loader
def load_user(user_id):

    db_user = db_interactions.get_user_by_id(user_id)

    user = User(id=db_user['id'], username=db_user['username'], password=db_user['password'], profile=db_user['profile'])

    utente['logged'] = True
    utente['username'] = db_user['username']

    return user


@app.route('/login_pescatore', methods=['POST'])
def login_pescatore():
    if request.method == 'POST':
        dati = request.form.to_dict()

        try:
            username = dati['username']
            password = dati['password']
        except KeyError:
            return redirect(url_for('login_page'))

        if not db_interactions.check_user_presence(username):
            app.logger.error('username non valido')
            return redirect(url_for('login_page'))

        if not check_password_hash(db_interactions.retrive_password(username), password):
            app.logger.error('password non valida per l\'account')
            return redirect(url_for('login_page'))

        utente['logged'] = True
        utente['username'] = username
        flash('Accesso Corretto')
        dati['password'] = generate_password_hash(password)
        dati['id'] = db_interactions.get_usr_id_by_username(username)
        dati['profile'] = db_interactions.get_usr_image(username)
        new = User(id=dati['id'], username=dati['username'], password=dati['password'], profile=dati['profile'])
        login_user(new, True)

    return redirect(url_for('home_page'))


@app.route('/iscriviti')
def prima_iscrizione():
    return render_template('iscriviti.html', user=utente)


@app.route('/iscrizione_utente_compilato', methods=['POST'])
def iscrizione_utente_compilato():
    if request.method == 'POST':
        dati = request.form.to_dict()

        try:
            username = dati['username']
            password = dati['password']
            image = request.files.to_dict()['image']
        except KeyError:
            return redirect(url_for('prima_iscrizione'))

        if username == ' ' or username == '' or db_interactions.check_user_presence(username):
            app.logger.error('username non valido')
            return redirect(url_for('prima_iscrizione'))

        if len(password) < 8 or not QOS.check_validity(password):
            app.logger.error('password non valida per l\'account')
            return redirect(url_for('prima_iscrizione'))

        utente['logged'] = True
        utente['username'] = username
        flash('Accesso Corretto')
        dati['password'] = generate_password_hash(password)
        dati['id'] = db_interactions.get_new_user_id()

        try:
            image = str(image).split("\'")[1]
            dati['profile'] = 'img/foto_profilo/'+image
            if image.split('.')[1] not in 'jpg png gif heif jpeg':
                raise ValueError
        except Exception:
            app.logger.error('Immagine di profilo non valida ')
            return redirect(url_for('prima_iscrizione'))

        db_interactions.insert_new_user(dati)
        new = User(id=dati['id'], username=dati['username'], password=dati['password'], profile=dati['profile'])
        login_user(new, True)

    return redirect(url_for('home_page'))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    utente['logged'] = False
    utente['username'] = ''
    return redirect(url_for('home_page'))
