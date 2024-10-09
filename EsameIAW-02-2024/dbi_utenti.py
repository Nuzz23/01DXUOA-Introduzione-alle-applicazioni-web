import sqlite3


# Funzione per prendere l'utente in tramite la sua mail
def get_user_by_email(email, PERCORSO):
    conn = sqlite3.connect(PERCORSO)
    c = conn.cursor()

    # classica query, nulla di speciale
    query = "SELECT * FROM UTENTE WHERE EMAIL = ?"

    # provo a convertire il risultato, da tupla a lista a dizionario
    try:
        c.execute(query, (email, ))
        row = c.fetchone()

        # converto e assegno i valori ai dati
        row = list(row)
        dati = {
            'EMAIL': row[0],
            'PASSWORD': row[1],
            'TELEFONO': row[2],
            'RUOLO': row[3],
            'NOME': row[4]
        }
        # se c'è un eccezione di qualsiasi tipo, non blocco il sito, ma la gestisco
    except Exception:
        dati = False

    c.close()
    conn.close()

    return dati


# Funzione per aggiungere un nuovo utente nella base dati
def registra_nuovo_utente(utente, PERCORSO):
    conn = sqlite3.connect(PERCORSO)
    cursor = conn.cursor()

    query = ("INSERT INTO UTENTE (EMAIL, PASSWORD, TELEFONO, RUOLO, NOME) "
             "VALUES (?,?,?,?,?)")

    # provo a eseguire l'inserimento e restituisco il relativo flag
    try:
        cursor.execute(query, (utente["EMAIL"], utente["PASSWORD"], utente["TELEFONO"], utente["RUOLO"],
                               utente["NOME"]))
        conn.commit()
        flag = True
    except Exception:
        conn.rollback()
        flag = False

    cursor.close()
    conn.close()
    return flag


# Controllo la presenza di un utente nella base dati tramite l'email
def check_user_presence_by_email(email, PERCORSO):
    conn = sqlite3.connect(PERCORSO)
    cursore = conn.cursor()

    query = "SELECT COUNT(*) FROM UTENTE WHERE EMAIL=?"

    # eseguo la query
    cursore.execute(query, (email, ))
    risultato = cursore.fetchone()

    # converto il risultato da tupla a intero
    try:
        risultato = int(list(risultato)[0])
    except ValueError:
        risultato = 0

    cursore.close()
    conn.close()
    return risultato


# Controlla la presenza di un utente tramite il nome scelto
def check_user_presence_by_name(nome, PERCORSO):
    conn = sqlite3.connect(PERCORSO)
    cursore = conn.cursor()
    query = "SELECT COUNT(*) FROM UTENTE WHERE UTENTE.NOME=?"

    # eseguo la queri e prendo un singolo risultato (sono sicuro ci sarà solo un utente con quel nome)
    cursore.execute(query, (nome,))
    risultato = cursore.fetchone()

    # provo a convertire il nome utente da tupla a intero
    try:
        risultato = int(list(risultato)[0])
    except ValueError:
        risultato = 0

    cursore.close()
    conn.close()

    return risultato


# Prendo la password dell'utente o tramite mail o tramite nome a seconda del tipo
def get_user_password(modo, tipo, PERCORSO):
    conn = sqlite3.connect(PERCORSO)
    cursore = conn.cursor()

    # Le due differenti query a seconda del metodo
    if tipo:
        query = "SELECT UTENTE.PASSWORD FROM UTENTE WHERE UTENTE.EMAIL=?"
    else:
        query = "SELECT UTENTE.PASSWORD FROM UTENTE WHERE UTENTE.NOME=?"

    # prendo il singolo risultato
    cursore.execute(query, (modo, ))
    risultato = cursore.fetchone()

    # lo converto da tupla a stringa
    try:
        risultato = str(list(risultato)[0])
    except ValueError:
        risultato = ''

    cursore.close()
    conn.close()
    return risultato


# Prendo l'username di un utente (univoco) data la mail dello stesso
def get_user_name_by_email(email, PERCORSO):
    conn = sqlite3.connect(PERCORSO)
    cursore = conn.cursor()

    query = "SELECT UTENTE.NOME FROM UTENTE WHERE UTENTE.EMAIL=?"

    try:
        cursore.execute(query, (email, ))
        risultato = str(list(cursore.fetchone())[0])
    except Exception:
        risultato = ' '

    cursore.close()
    conn.close()
    return risultato


def get_user_by_name(nome, PERCORSO):
    conn = sqlite3.connect(PERCORSO)
    c = conn.cursor()

    query = "SELECT * FROM UTENTE WHERE NOME = ?"

    try:
        c.execute(query, (nome,))
        row = c.fetchone()

        row = list(row)
        dati = {
            'EMAIL': row[0],
            'PASSWORD': row[1],
            'TELEFONO': row[2],
            'RUOLO': row[3],
            'NOME': row[4]
        }
    except Exception:
        dati = False

    c.close()
    conn.close()

    return dati
