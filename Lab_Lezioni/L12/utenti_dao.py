import sqlite3


def get_user_by_id(usr_id):
    query = 'SELECT * FROM UTENTI WHERE UTENTI.ID=?'
    connection = sqlite3.connect('database/mangiato.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(query, (usr_id, ))

    result = cursor.fetchone()
    print(result)

    cursor.close()
    connection.close()

    return result


def add_user(user):
    query = 'INSERT INTO UTENTI(ID, NOME, COGNOME, EMAIL, PASSWORD) VALUES (?,?,?,?,?)'

    connection = sqlite3.connect('database/mangiato.db')
    cursor = connection.cursor()

    success = False

    cursor.execute('SELECT COUNT(*) FROM UTENTI')
    if int(list(cursor.fetchone())[0]):
        cursor.execute('SELECT MAX(ID) FROM UTENTI')
        idf = int(list(cursor.fetchone())[0])
    else:
        idf = 0

    try:
        cursor.execute(query, (idf+1, user['nome'], user['cognome'], user['email'], user['password'], ))
        connection.commit()
        success = True
    except Exception as e:
        print('Error', str(e))
        connection.rollback()

    cursor.close()
    connection.close()

    return success


def cerca_utente(mail):
    query = 'SELECT COUNT(*) FROM UTENTI WHERE UTENTI.EMAIL = ?'

    connection = sqlite3.connect('database/mangiato.db')
    cursor = connection.cursor()

    cursor.execute(query, (mail, ))

    if int(list(cursor.fetchone())[0]):
        success = True
    else:
        success = False

    cursor.close()
    connection.close()

    return success


def getutentebymail(mail):
    query = 'SELECT * FROM UTENTI WHERE UTENTI.EMAIL = ?'

    connection = sqlite3.connect('database/mangiato.db')
    cursor = connection.cursor()

    cursor.execute(query, (mail, ))

    x = list(cursor.fetchone())

    utente = {
        "id": x[0],
        "nome": x[1],
        "cognome": x[2],
        "email": x[3],
        "password": x[4]
    }

    cursor.close()
    connection.close()

    return utente

