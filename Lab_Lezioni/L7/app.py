from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def index():
    first_plates = [{'id': 1, 'name': 'Pasta al tonno'},
            {'id': 2, 'name': 'Lasagne'},
            {'id': 3, 'name': 'Pasta al sugo'},
            {'id': 4, 'name': 'Pasta alla carbonara'}]
    return render_template('index.html', first=first_plates)


@app.route('/about.html')
def about():
    return render_template('about.html')