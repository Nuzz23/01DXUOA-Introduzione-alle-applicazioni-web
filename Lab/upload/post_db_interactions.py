import sqlite3


def fetch_posts():
    query = "SELECT * FROM POST ORDER BY ID"

    connessione = sqlite3.connect("base_dati/base_di_dati.db")
    cursore = connessione.cursor()
    connessione.row_factory = sqlite3.SQLITE_ROW

    cursore.execute(query)
    risultati = cursore.fetchall()

    riporta = list()
    if len(risultati):
        for tupla in risultati:
            tupla = list(tupla)

            query = "SELECT username, immagine_profilo FROM UTENTI WHERE id =?"

            cursore.execute(query, (tupla[4], ))
            info = list(cursore.fetchone())

            try:
                tupla[6] = (tupla[int(6)]).split(':')[0]
                tupla[3].split('/')
            except AttributeError:
                tupla[6] = '*'
                tupla[3] = '*'
                tupla[7] = '*'
                tupla[8] = '*'

            post = {
                "id": tupla[0],
                "date": tupla[1],
                "text": tupla[2],
                "image": tupla[3],
                "username": info[0],
                "profile": info[1],
                "likes": tupla[5],
                "type": tupla[6].upper(),
                "weight": tupla[7],
                "length": tupla[8],
                "location": tupla[9]
            }
            riporta.append(post)
    cursore.close()
    connessione.close()
    """
    for i in range(len(riporta)):
        max_data = '0'
        posmax = 0
        for j in range(i, len(riporta)):
            if max_data < ''.join(riporta[j]["date"].split('-')[::-1]):
                max_data = ''.join(riporta[j]["date"].split('-')[::-1])
                posmax = j
        if posmax != i:
            tmp = riporta[i]
            riporta[i] = riporta[int(posmax)]
            riporta[posmax] = tmp
    """
    return riporta


def inserisci_nuovo_post(nuovo):

    connessione = sqlite3.connect("base_dati/base_di_dati.db")
    cursore = connessione.cursor()

    query = "SELECT ID FROM UTENTI WHERE username = ?"

    cursore.execute(query, (nuovo["username"],))

    idu = int(list(cursore.fetchone())[0])

    query = "SELECT MAX(ID) FROM POST"

    cursore.execute(query)
    try:
        idp = int(list(cursore.fetchone())[0])+1
    except TypeError:
        idp = 1
    query = ("INSERT INTO POST(ID, DATA, TESTO, IMAGE, ID_UTENTE, LIKES, TYPE, WEIGHT, LENGTH) "
             "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)")

    cursore.execute(query, (idp, nuovo['date'], nuovo['text'], nuovo['image'], idu, nuovo['likes'],
                            nuovo['type'], nuovo['weight'], nuovo['length']))

    try:
        connessione.commit()
    except Exception:
        connessione.rollback()
        cursore.close()
        connessione.close()
        return False

    cursore.close()
    connessione.close()
    return True
