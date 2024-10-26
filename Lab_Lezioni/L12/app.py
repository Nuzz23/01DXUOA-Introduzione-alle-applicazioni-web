# import module
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_session import sessions
import piatti_dao
from models import User
import utenti_dao


# create the application
app = Flask(__name__)
app.config["SECRET_KEY"] = 'DAMMI TRE PAROLE SOLE CUORE E AMORE, NO SCHERZAVO SEI FROCIO'

login_manager = LoginManager()
login_manager.init_app(app)


# define the homepage
@app.route('/')
def index():
    piatti_db = piatti_dao.get_piatti()
    return render_template('index.html', piatti=piatti_db)


@app.route('/piatti/<int:id>')
def piatto_singolo(id):
    piatto_db = piatti_dao.get_piatto(id)
    recensioni_db = piatti_dao.get_recensioni(id)
    return render_template('single.html', piatto=piatto_db, recensioni=recensioni_db)


# define the about page
@app.route('/about')
def about():
    return render_template('about.html')


# define the signup page
@app.route('/iscriviti')
def signup():
    return render_template('signup.html')


@app.route('/recensioni/new', methods=['POST'])
@login_required
def add_recensione():

    recensione = request.form.to_dict()

    if recensione['recensione'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('index'))

    foto = request.files['imgRecensione']
    if foto.filename != '':
        foto.save('static/'+foto.filename)
        recensione['url_foto'] = foto.filename

    rec = {'testo_recensione': 'test', 'url_foto': 'test_url', 'valutazione': 4, 'piatto': 1}
    piatti_dao.add_recensione(rec)

    return redirect(url_for('index'))


@login_manager.user_loader
def load_user(user_id):

    db_user = utenti_dao.get_user_by_id(user_id)

    user = User(id=db_user['id'], nome=db_user['nome'], cognome=db_user['cognome'], email=db_user['email'],
                password=db_user['password'])

    return user


@app.route('/iscriviti', methods=['POST'])
def iscriviti():

    new_user_from_form = request.form.to_dict()

    if new_user_from_form['nome'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('index'))

    if new_user_from_form['cognome'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('index'))

    if new_user_from_form['email'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('index'))

    if new_user_from_form['password'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('index'))

    success = utenti_dao.add_user(new_user_from_form)

    if success:
        return redirect(url_for('index'))
    return redirect(url_for('iscriviti'))


@app.route('/login', methods=['POST'])
def login():
    utente_form = request.form.to_dict()

    utente = utenti_dao.cerca_utente(utente_form['email'])

    if not utente:
        print("Non esiste l'utente")
        return redirect(url_for('index'))
    else:
        utente_form = utenti_dao.getutentebymail(utente_form['email'])
        new = User(id=utente_form['id'], nome=utente_form['nome'], cognome=utente_form['cognome'],
                   email=utente_form['email'], password=utente_form['password'])
        login_user(new, True)
        print("Success")

        return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
