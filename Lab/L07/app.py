from flask import Flask, render_template, request
import os
from random import randint
import datetime

LETTURA = 'r'

app = Flask(__name__)


@app.context_processor
def inject_today_date():
    return {'today_date': datetime.date.today()}


def randomization():
    users = open("static/img/utenti.txt", LETTURA)
    utenti = list()

    for utente in users:
        utenti.append(utente)

    users.close()

    tmp = open("static/img/descrizione_post.txt", LETTURA)
    descrizioni = list()

    for descrizione in tmp:
        descrizioni.append(descrizione)
    tmp.close()

    tmp = open("static/img/location.txt", LETTURA)
    posizione = list()

    for descrizione in tmp:
        posizione.append(descrizione)
    tmp.close()

    val = randint(1, len(descrizioni) // 2)
    mkdir = (r"C:\Users\utente\OneDrive\Desktop\polito\Casa\3 anno\introduzione alle applicazioni web\L05-True\static"
             r"\img\pesci")
    file = list()

    for path in os.listdir(mkdir):
        if os.path.isfile(os.path.join(mkdir, path)):
            file.append(r"img/pesci/" + path)

    mkdir = (r"C:\Users\utente\OneDrive\Desktop\polito\Casa\3 anno\introduzione alle applicazioni web\L05-True\static"
             r"\img\foto_profilo")
    profilepp = list()

    for path in os.listdir(mkdir):
        if os.path.isfile(os.path.join(mkdir, path)):
            profilepp.append(r"img/foto_profilo/" + path)

    lista_post = list()

    for i in range(0, val):
        tmp = randint(0, len(file) - 1)
        testo = [item for item in descrizioni if (((file[tmp].split("/"))[-1]).split('.'))[0].upper() in item.upper()][0].strip()
        mese = randint(1, 11)
        if mese == 2:
            giorno = randint(1, 28)
        elif mese in {11, 4, 6, 9}:
            giorno = randint(1, 30)
        else:
            giorno = randint(1, 31)

        post = {
            "username": utenti[randint(0, len(utenti) - 1)].strip(),
            "date": str(giorno) + '-' + str(mese) + '-' + "2023",
            "image": file[tmp],
            "text": testo,
            "profile": profilepp[randint(0, len(profilepp) - 1)],
            "likes": randint(0, 20000),
            "location": posizione[randint(0, len(posizione)-1)],
            "weight": randint(30, 500)/100,
            "lenght": randint(100, 600)/10,
            "type": testo.split(":")[0]
        }
        lista_post.append(post)

    return lista_post


def comments(ele_posts, num):
    users = open("static/img/utenti.txt", LETTURA)
    utenti = list()

    for utente in users:
        utenti.append(utente)

    users.close()

    tmp = open("static/img/commenti.txt", LETTURA)
    commenti = list()

    for descrizione in tmp:
        commenti.append(descrizione)
    tmp.close()

    mkdir = (r"C:\Users\utente\OneDrive\Desktop\polito\Casa\3 anno\introduzione alle applicazioni web\L05-True\static"
             r"\img\foto_profilo")
    profilepp = list()

    for path in os.listdir(mkdir):
        if os.path.isfile(os.path.join(mkdir, path)):
            profilepp.append(r"img/foto_profilo/" + path)

    lista_commenti = list()

    for i in range(0, num):
        lista_post = list()
        numcommenti = randint(0, len(commenti) // 2 + 1)
        for j in range(0, numcommenti):
            mese = randint(int(ele_posts[i]["date"].split("-")[1]), 12)
            if mese == int(ele_posts[i]["date"].split("-")[1]):
                giorno = randint(int(ele_posts[i]["date"].split("-")[0]), 31)
            elif mese == 2:
                giorno = randint(1, 28)
            elif mese in {11, 4, 6, 9}:
                giorno = randint(1, 30)
            else:
                giorno = randint(1, 31)

            commento = {
                "username": [utente for utente in utenti if utente != ele_posts[i]["username"]][randint(0, len([utente for utente in utenti if utente != posts[i]["username"]])-1)],
                "date": str(giorno) + '-' + str(mese) + '-' + "2023",
                "text": commenti[randint(0, len(commenti)-1)],
                "profile": [profile for profile in profilepp if profile != ele_posts[i]["profile"]][randint(0, len([profile for profile in profilepp if profile != posts[i]["profile"]])-1)],
                "like": randint(0, 100)
            }
            lista_post.append(commento)
        lista_commenti.append([lista_post, numcommenti])

    return lista_commenti


posts = randomization()
numpost = [len(posts)]
comm = comments(posts, numpost[0])


@app.route('/nuovo_post/', methods=['GET', 'POST'])
def nuovo_post():
    if request.method == 'POST':
        nuovo = request.form.to_dict()
        users = list()
        for i in range(0, numpost[0]):
            if posts[i]["username"] not in users:
                users.append(posts[i]["username"])

        nuovo['username'] = users[int(nuovo['username'])]

        if len(nuovo['text']) < 30 or len(nuovo['text']) > 200:
            app.logger.error('Lunghezza del post non valida')
            return render_template("Home.html", lista_post=posts, numpost=numpost[0])
        if str(nuovo['date']) > str(inject_today_date()['today_date']):
            app.logger.error('Peschi nel futuro?')
            return render_template("Home.html", lista_post=posts, numpost=numpost[0])

        profilo = list()
        for i in range(0, numpost[0]):
            if posts[i]["username"] == nuovo["username"]:
                profilo.append(posts[i]["profile"])
        profilo = profilo[0]

        nuovo["profile"] = profilo

        if "." in nuovo["image"]:
            foto = "img/pesci/" + str(nuovo['image'])
        else:
            foto = '*'

        if foto != '*' and str(foto.split('.')[1]) not in "jpeg jpg png heif":
            app.logger.error('Non una foto')
            return render_template("Home.html", lista_post=posts, numpost=numpost[0])

        nuovo["image"] = foto

        if foto != '*':
            data = nuovo["date"].split('-')
        else:
            data = str(inject_today_date()['today_date']).split('-')

        date = ""
        for i in range(len(data)-1, -1, -1):
            date = date+data[i] + '-'

        nuovo["date"] = date[0:len(date)-1:1]
        nuovo["likes"] = randint(0, 10)

        tmp = open("static/img/location.txt", LETTURA)
        posizione = list()

        for descrizione in tmp:
            posizione.append(descrizione.strip())
        tmp.close()

        nuovo["location"] = posizione[randint(0, len(posizione)-1)]
        nuovo["weight"] = randint(30, 500) / 100
        nuovo["lenght"] = randint(100, 600) / 10
        if foto != '*':
            nuovo["type"] = "<b> " + foto.split('/')[-1].split('.')[0].upper() + " </b>"
        else:
            nuovo["type"] = "*"

        posts.append(nuovo)
        numpost[0] = numpost[0] + 1
        comm.append([[], 0])

        return render_template("Home.html", lista_post=posts, numpost=numpost[0])
    else:
        return render_template("Home.html", lista_post=posts, numpost=numpost[0])


@app.route('/')
def home_page():
    return render_template("Home.html", lista_post=posts, numpost=numpost[0])


@app.route('/post/<int:id>')
def postato(id):
    return render_template("post.html", post=posts[id-1], commenti_post=comm[id-1][0], numcommenti=comm[id-1][1])


@app.route('/Chi_Siamo.html')
def chi_siamo():
    mkdir = (r"C:\Users\utente\OneDrive\Desktop\polito\Casa\3 anno\introduzione alle applicazioni web\L05-True\static"
             r"\img\personali")
    file = list()

    for path in os.listdir(mkdir):
        if os.path.isfile(os.path.join(mkdir, path)):
            file.append(r"img/personali/"+path)

    return render_template("Chi_Siamo.html", immagine=file[randint(0, len(file)-1)])
