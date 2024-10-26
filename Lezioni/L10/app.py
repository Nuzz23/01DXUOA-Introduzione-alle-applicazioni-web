from flask import Flask, render_template, request, redirect

app = Flask(__name__)

recensioni = list()


@app.route('/')
def index():
    first_plates = [{'id': 1, 'name': 'Pasta al tonno'}, {'id': 2, 'name': 'Lasagne'}, {'id': 3, 'name': 'Pasta al sugo'}]

    return render_template('index.html', first=first_plates)


@app.route('/recensioni/new', methods=['POST'])
def new():
    recensione = request.form.to_dict()
    if recensione['NomeCognome'] == '':
        app.logger.error('errore')
    else:
        app.logger.info(recensione['NomeCognome'])

    if recensione['Matricola'] == '':
        app.logger.error('errore')
    else:
        app.logger.info(recensione['Matricola'])
        print(recensione['Matricola'])

    if recensione['Recensione'] == '':
        app.logger.error('errore')
    else:
        app.logger.info(recensione['Recensione'])
        print(recensione['Recensione'])

    if recensioni:
        recensione['id'] = recensioni[-1]['id']+1
    else:
        recensione['id'] = 1
    recensioni.append(recensione)

    foto = request.files['Piatto']
    foto.save('static', foto.filename)

    recensione['url_foto'] = foto.filename
    recensione['id'] = recensioni[-1]['id']+1

    recensioni.append(recensione)

    return redirect('/')


@app.route('/recensioni')
def recensio():
    return render_template('recensioni.html', recensioni=recensioni)
