# import module
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

# create the application
app = Flask(__name__)

menu = [
  {'type': 'Primi', 'plates': [{'name': 'pasta al tonno', 'promotion': True}, {'name': 'pasta al sugo'}]},
  {'type': 'Secondi', 'plates': [{'name': 'tonno', 'promotion': True}, {'name': 'cotoletta'}]},
  {'type': 'Contorni', 'plates': [{'name': 'fagiolini'}, {'name': 'patate al forno'}]},
  ]

recensioni = [{'id': 0, 'recensione': 'Recensione 0'}]


# define the homepage
@app.route('/')
def index():
    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()
    conn.row_factory = sqlite3.SQLITE_ROW

    cursor.execute("SELECT * FROM PIATTI")

    piatto_db = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('index.html', piatto=piatto_db, recensioni=recensioni)


# define the about page
@app.route('/about')
def about():
    return render_template('about.html')


# define the page of each first plates
@app.route('/first/<int:id>')
def first_plate(id):  # indice del piatto nell'array "plates"
    plate = menu[0]['plates'][id-1]
    return render_template('single.html', plate=plate)


@app.route('/recensioni/new', methods=['POST'])
def add_recensione():

    recensione = request.form.to_dict()

    if recensione['recensione'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('index'))

    foto = request.files['imgRecensione']
    if foto.filename != '':
        foto.save('static/'+foto.filename)
        recensione['url_foto'] = foto.filename

    recensione['id'] = recensioni[-1]['id'] + 1

    recensioni.append(recensione)

    app.logger.info(recensione)

    return redirect(url_for('index'))
