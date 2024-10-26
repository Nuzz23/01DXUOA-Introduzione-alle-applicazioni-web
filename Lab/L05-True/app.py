from flask import Flask, render_template
import os
from random import randint

LETTURA = 'r'

app = Flask(__name__)


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

    numpost = randint(1, len(descrizioni) // 2)
    mkdir = r"C:\Users\utente\OneDrive\Desktop\polito\Casa\3 anno\introduzione alle applicazioni web\L05-True\static\img\pesci"
    file = list()

    for path in os.listdir(mkdir):
        if os.path.isfile(os.path.join(mkdir, path)):
            file.append(r"img/pesci/" + path)

    mkdir = r"C:\Users\utente\OneDrive\Desktop\polito\Casa\3 anno\introduzione alle applicazioni web\L05-True\static\img\foto_profilo"
    profilepp = list()

    for path in os.listdir(mkdir):
        if os.path.isfile(os.path.join(mkdir, path)):
            profilepp.append(r"img/foto_profilo/" + path)

    lista_post = list()

    for i in range(0, numpost):
        tmp = randint(0, len(file) - 1)
        testo=[item for item in descrizioni if (((file[tmp].split("/"))[-1]).split('.'))[0].upper() in item.upper()][0].strip()
        post = {
            "username": utenti[randint(0, len(utenti) - 1)].strip(),
            "date": randint(1, 96),
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

    lista_post2 = list()
    pos = 0
    for i in range(0, len(lista_post)):
        minimo = 999999999
        for j in range(0, len(lista_post)):
            if lista_post[j]["date"] < minimo:
                if len(lista_post2) == 0 or (lista_post[j]["date"] > lista_post2[-1]["date"]):
                    minimo = lista_post[j]["date"]
                    pos = j
        lista_post2.append(lista_post[pos])

    return lista_post2


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

    mkdir = r"C:\Users\utente\OneDrive\Desktop\polito\Casa\3 anno\introduzione alle applicazioni web\L05-True\static\img\foto_profilo"
    profilepp = list()

    for path in os.listdir(mkdir):
        if os.path.isfile(os.path.join(mkdir, path)):
            profilepp.append(r"img/foto_profilo/" + path)

    lista_commenti = list()

    for i in range(0, num):
        lista_post = list()
        numcommenti = randint(0, len(commenti) // 2 + 1)
        for j in range(0, numcommenti):
            commento = {
                "username": [utente for utente in utenti if utente != ele_posts[i]["username"]][randint(0, len([utente for utente in utenti if utente != posts[i]["username"]])-1)],
                "date": randint(1, ele_posts[i]["date"]),
                "text": commenti[randint(0, len(commenti)-1)],
                "profile": [profile for profile in profilepp if profile != ele_posts[i]["profile"]][randint(0, len([profile for profile in profilepp if profile != posts[i]["profile"]])-1)],
                "like": randint(0, 100)
            }
            lista_post.append(commento)
        lista_commenti.append([lista_post, numcommenti])

    return lista_commenti


posts = randomization()
numpost = len(posts)
comm = comments(posts, numpost)

a=1
@app.route('/')
def home_page():
    return render_template("Home.html", lista_post=posts, numpost=numpost)


@app.route('/post/<int:id>')
def postato(id):
    return render_template("post.html", post=posts[id-1], commenti_post=comm[id-1][0], numcommenti=comm[id-1][1])


@app.route('/Chi_Siamo.html')
def Chi_Siamo():
    mkdir = r"C:\Users\utente\OneDrive\Desktop\polito\Casa\3 anno\introduzione alle applicazioni web\L05-True\static\img\personali"
    file = list()

    for path in os.listdir(mkdir):
        if os.path.isfile(os.path.join(mkdir, path)):
            file.append(r"img/personali/"+path)

    return render_template("Chi_Siamo.html", immagine=file[randint(0, len(file)-1)])


