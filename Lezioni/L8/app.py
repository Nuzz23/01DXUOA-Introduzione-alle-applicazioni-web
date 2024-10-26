# import module
from flask import Flask, render_template

# create the application
app = Flask(__name__)

menu = [{"type": "Primi", "plates": [{"name": "Pasta al Tonno", 'promotion': True}, {"name": "Pasta al Sugo"}]},
        {"type": "Secondi", "plates": [{"name": "Cotoletta"}, {"name": "Tonno", 'promotion': True}]},
        {"type": "Contorni", "plates": [{"name": "Fagiolini"}, {"name": "Patate"}]}]

# define the homepage
@app.route('/')
def index():
    return render_template('index.html', menu=menu)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/first/<int:id>")
def first_plate(id):        # indice del piatto nell'array plates
    return render_template("single.html", plate=menu[0]["plates"][id-1])

