import sqlite3


def fetch_commenti(id):
    connessione = sqlite3.connect('base_dati/base_di_dati.db')
    cursore = connessione.cursor()

    query = ("SELECT * "
             "FROM COMMENTI "
             "WHERE ID_POST = ?")

    cursore.execute(query, (id+1, ))
    ris = cursore.fetchall()

    risultati = list()
    for risultato in ris:
        if type(risultato) is not dict:
            risultato = list(risultato)
            query = "SELECT username, immagine_profilo FROM UTENTI WHERE id =?"

            cursore.execute(query, (risultato[1],))
            info = list(cursore.fetchone())

            if risultato[2] is None:
                risultato[2] = '*'

            diz = {
                "username": info[0],
                "likes": risultato[4],
                "image": risultato[2],
                "text": risultato[5],
                "stars": risultato[3],
                "profile": info[1],
                "date": risultato[7]
            }

            risultati.append(diz)

    cursore.close()
    connessione.close()
    return risultati


def check_user(nome):
    connessione = sqlite3.connect('base_dati/base_di_dati.db')
    cursore = connessione.cursor()

    query = 'SELECT COUNT(*) FROM UTENTI WHERE UTENTI.username = ?'

    cursore.execute(query, (nome, ))
    res = cursore.fetchone()

    try:
        if int(list(res)[0]):
            booleano = True
        else:
            booleano = False
    except ValueError:
        booleano = False

    cursore.close()
    connessione.close()
    return booleano


def add_comment(commento, post, usr):
    query = "INSERT INTO COMMENTI(ID, ID_UTENTE, IMAGE, STARS, LIKES, TEXT, ID_POST, DATA) VALUES (?,?,?,?,?,?,?,?)"
    connessione = sqlite3.connect('base_dati/base_di_dati.db')
    cursore = connessione.cursor()

    if commento['username'] == usr:
        id_utente = 0
    else:
        cursore.execute("SELECT ID FROM UTENTI WHERE UTENTI.USERNAME=?", (commento['username'], ))
        id_utente = int(list(cursore.fetchone())[0])

    cursore.execute("SELECT MAX(ID) FROM COMMENTI")

    try:
        idc = 1+int(list(cursore.fetchone())[0])
    except TypeError:
        idc = 1

    try:
        cursore.execute(query, (idc, id_utente, commento['image'], commento['valutazione'],
                                           commento['likes'], commento['text'], post, commento['date']))
        connessione.commit()
    except Exception:
        connessione.rollback()

    cursore.close()
    connessione.close()
