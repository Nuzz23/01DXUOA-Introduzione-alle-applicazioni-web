import sqlite3


def fetch_chi_siamo_image():
    connessione = sqlite3.connect('base_dati/base_di_dati.db')
    cursore = connessione.cursor()

    query = "SELECT * FROM CHI_SIAMO_IMAGES"

    cursore.execute(query)
    immagini = cursore.fetchall()

    images = list()

    for immagine in immagini:
        images.append(str(immagine).split("'")[1])

    cursore.close()
    connessione.close()
    return images


def get_usr_image(usr):
    connessione = sqlite3.connect('base_dati/base_di_dati.db')
    cursore = connessione.cursor()

    query = "SELECT immagine_profilo FROM UTENTI WHERE UTENTI.USERNAME=?"

    cursore.execute(query, (usr, ))
    immagine = str(list(cursore.fetchone())[0])

    cursore.close()
    connessione.close()
    return immagine


def check_user_presence(user_name):
    connessione = sqlite3.connect('base_dati/base_di_dati.db')
    cursore = connessione.cursor()

    query = "SELECT COUNT(*) FROM UTENTI WHERE UTENTI.USERNAME=?"

    cursore.execute(query, (user_name,))
    presence = int(list(cursore.fetchone())[0])

    cursore.close()
    connessione.close()
    return presence


def get_usr_by_id(idu):
    connessione = sqlite3.connect('base_dati/base_di_dati.db')
    cursore = connessione.cursor()

    query = "SELECT username FROM UTENTI WHERE UTENTI.ID=?"

    cursore.execute(query, (idu,))
    try:
        x = cursore.fetchone()
        x = list(x)
        x = x[0]
        presence = str(x)
    except Exception:
        presence = -1

    cursore.close()
    connessione.close()
    return presence


def retrive_password(username):
    connessione = sqlite3.connect('base_dati/base_di_dati.db')
    cursore = connessione.cursor()

    query = "SELECT PASSWORD FROM UTENTI WHERE UTENTI.username=?"

    cursore.execute(query, (username, ))

    ris = cursore.fetchone()

    cursore.close()
    connessione.close()

    try:
        return list(ris)[0]
    except Exception:
        return 0


def get_usr_id_by_username(username):
    connessione = sqlite3.connect('base_dati/base_di_dati.db')
    cursore = connessione.cursor()

    query = "SELECT ID FROM UTENTI WHERE UTENTI.username=?"

    cursore.execute(query, (username, ))

    ris = cursore.fetchone()

    cursore.close()
    connessione.close()

    try:
        return int(list(ris)[0])
    except Exception:
        return -1


def get_new_user_id():
    connessione = sqlite3.connect('base_dati/base_di_dati.db')
    cursore = connessione.cursor()

    query = "SELECT MAX(ID) FROM UTENTI"

    cursore.execute(query)

    ris = cursore.fetchone()

    cursore.close()
    connessione.close()

    try:
        return int(list(ris)[0])+1
    except Exception:
        return 1


def insert_new_user(dati):
    connessione = sqlite3.connect('base_dati/base_di_dati.db')
    cursore = connessione.cursor()

    query = "INSERT INTO UTENTI(ID, USERNAME, PASSWORD, IMMAGINE_PROFILO) VALUES (?,?,?,?)"

    try:
        cursore.execute(query, (dati['id'], dati['username'], dati['password'], dati['profile']))
        connessione.commit()
    except Exception:
        connessione.rollback()

    cursore.close()
    connessione.close()


def get_user_by_id(user_id):
    connessione = sqlite3.connect('base_dati/base_di_dati.db')
    cursore = connessione.cursor()

    query = "SELECT * FROM UTENTI WHERE UTENTI.ID=?"

    cursore.execute(query, (user_id, ))
    ris = cursore.fetchone()

    cursore.close()
    connessione.close()

    try:
        ris = list(ris)
        riporta = {
            'id': int(ris[0]),
            'username': ris[1],
            'password': ris[2],
            'profile': ris[3]
        }
        return riporta
    except Exception:
        return False
