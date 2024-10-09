import sqlite3


# Email di default per esercizi eliminati
ANONIMO_EMAIL = "Anonimo"


# Controllo la presenza della mail dell'utente all'interno della base dati
def controllo_presenza_utente(email, percorso):
    # Mi collego al database
    conn = sqlite3.connect(percorso)
    cursore = conn.cursor()

    # Query
    query = "SELECT COUNT(*) FROM UTENTE WHERE EMAIL=?"

    # Eseguo la questi e ne controllo il risultato (1 se c'è, 0 altrimenti)
    try:
        cursore.execute(query, (email,))
        risultato = cursore.fetchone()
        risultato = int(list(risultato)[0])
    except ValueError:
        risultato = 0

    cursore.close()
    conn.close()
    return risultato


# Controllo che la password data al login sia corretta
def password_corretta(email, percorso):
    # Mi collego alla base dati
    conn = sqlite3.connect(percorso)
    cursore = conn.cursor()

    # prendo la password salvata nella base dati
    query = "SELECT UTENTE.PASSWORD FROM UTENTE WHERE UTENTE.EMAIL=?"

    try:
        # prendo il singolo risultato
        cursore.execute(query, (email,))
        risultato = cursore.fetchone()
        risultato = str(list(risultato)[0])
    except ValueError:
        risultato = ''

    cursore.close()
    conn.close()
    return risultato


# ottengo i dati di un dato utente
def get_dati_utente(email, PERCORSO):
    # Controllo che la mail sia diversa da quella associata all'utente anonimo (da gestire a parte)
    if email != ANONIMO_EMAIL:
        # mi connetto alla base dati
        conn = sqlite3.connect(PERCORSO)
        c = conn.cursor()

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
                'NOME': row[2],
                'COGNOME': row[3],
                'RUOLO': row[4]
            }
        except Exception:
            dati = False

        c.close()
        conn.close()
    else:
        # In caso di utente anonimo servono solo questi dati
        dati = {
            'EMAIL': ANONIMO_EMAIL,
            'NOME': "Utente",
            "COGNOME": "anonimo"
        }

    return dati


# Controlla la presenza di un utente nella base dati data la mail
def controlla_mail_presente(email, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursore = conn.cursor()

    query = "SELECT COUNT(*) FROM UTENTE WHERE EMAIL=?"

    # eseguo la query
    cursore.execute(query, (email,))
    risultato = cursore.fetchone()

    # converto il risultato da tupla a intero
    try:
        risultato = int(list(risultato)[0])
    except ValueError:
        risultato = 0

    cursore.close()
    conn.close()
    return risultato


# Controlla la correttezza di tutti i campi forniti durante la registrazione
# 0 = no errore, 1 = errore generico, 2 = email duplicata
def controlla_nuovo_utente(dati, PERCORSO):
    # Controllo la mail:
    # lunghezza
    # assenza di spazi (se non a inizio o a fine mail)
    # la presenza di . e @
    if ('@' not in dati['EMAIL'] or '.' not in dati['EMAIL'] or len(dati['EMAIL']) < 8 or len(dati['EMAIL']) > 40
            or ' ' in dati['EMAIL'].strip()):
        return 1

    # Controllo che la mail non sia già in uso
    if controlla_mail_presente(dati['EMAIL'], PERCORSO):
        return 2

    # Controllo la password:
    # lunghezza corretta
    # assenza di spazi
    if len(dati['PASSWORD']) < 8 or len(dati['PASSWORD']) > 50 or ' ' in dati['PASSWORD']:
        return 1

    # Controllo la correttezza del nome tramite la lunghezza
    # e l'assenza di numeri
    if not (4 <= len(dati['NOME']) <= 40) or stringa_contiene_numeri(dati['NOME']):
        return 1
    
    # Controllo la correttezza del cognome tramite la lunghezza
    # e l'assenza di numeri
    if not (4 <= len(dati['COGNOME']) <= 40) or stringa_contiene_numeri(dati['COGNOME']):
        return 1

    # Controllo la correttezza dell'errore
    try:
        if int(dati['RUOLO']) != 1 and int(dati["RUOLO"]) != 0:
            raise ValueError
    except ValueError or KeyError:
        return 1

    return 0


# Controllo la presenza di numeri in una stringa
def stringa_contiene_numeri(stringa):
    for c in stringa:
        if c in '0123456789':
            return True

    return False


# Inserisce un nuovo utente nella base dati
def inserisci_nuovo_utente(dati, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()

    query = ("INSERT INTO UTENTE (EMAIL, PASSWORD, NOME, RUOLO, COGNOME) "
             "VALUES (?,?,?,?,?)")

    # provo l'inserimento
    try:
        cursor.execute(query, (dati["EMAIL"], dati["PASSWORD"], dati["NOME"], int(dati["RUOLO"]),
                               dati["COGNOME"]))
        # Rendo permanenti i cambiamenti
        conn.commit()
        flag = True
    except Exception:
        conn.rollback()
        flag = False

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return flag


# Controllo se il cliente non ha un personal trainer assegnato
def cliente_cerca_personal(email, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()

    # Controllo se il cliente non è presente in assunzione
    query = "SELECT COUNT(*) FROM ASSUNZIONE WHERE CLIENTE=?"
    try:
        cursor.execute(query, (email, ))
        if not int(list(cursor.fetchone())[0]):
            flag = True
        else:
            raise Exception
    except Exception:
        flag = False

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return flag


# Trovo tutti i personal trainer nella mia applicazione
def trova_tutti_personal_trainer(percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()

    elenco = list()

    # Trovo tutti i personal trainer presenti
    query = "SELECT * FROM UTENTE WHERE RUOLO=?"
    try:
        cursor.execute(query, (1,))
        for row in list(cursor.fetchall()):
            elenco.append({"EMAIL": row[0], "NOME": row[2], "COGNOME": row[3],
                           "RATING": ranking_allenatore(row[0], percorso)})

    except Exception:
        elenco = list()

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return elenco


# Trovo il personal trainer di un dato cliente
def trova_personal_dato_cliente(email, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()

    # Trovo il personal associato al cliente (se lo ha)
    query = "SELECT ALLENATORE FROM ASSUNZIONE WHERE CLIENTE=?"
    try:
        cursor.execute(query, (email, ))
        dati = get_dati_utente(list(cursor.fetchone())[0], percorso)
        dati['RATING'] = ranking_allenatore(dati['EMAIL'], percorso)
    except Exception:
        dati = False

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return dati


# Assegno a un cliente un personal trainer
def assegna_personal(cliente_email, personal_email, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()

    query = "INSERT INTO ASSUNZIONE(CLIENTE, ALLENATORE) VALUES (?,?)"

    # Provo ad assegnare l'allenatore al cliente
    try:
        cursor.execute(query, (cliente_email, personal_email))
        # Rendo permanenti i cambiamenti
        conn.commit()
        flag = True
    except Exception:
        flag = False
        conn.rollback()

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return flag


# Controlla che i dati inseriti per creare un nuovo esercizio siano corretti
# funzione configurata per gestire errori multipli anziché un return immediato
def valida_nuovo_esercizio(dati):
    errore = '0'

    # titolo corretto e senza caratteri strani
    if 5 <= len(dati["TITOLO"]) <= 50:
        for c in dati["TITOLO"]:
            if str(c).lower() not in "0123456789abcdefghijklmnopqrstuvwxyz _":
                errore = '1'
                break
    else:
        errore = '1'

    # descrizione lunga il giusto
    if len(dati["DESC"]) < 5 or len(dati["DESC"]) > 200:
        errore = errore + '1'
    else:
        errore = errore + '0'

    # difficoltà tra i valori compresi (0=facile, 1=medio, 2=difficile)
    try:
        dati["DIFF"] = int(dati["DIFF"])
        if dati["DIFF"] < 0 or dati["DIFF"] > 2:
            raise ValueError
    except ValueError:
        errore = ''

    # visibilità tra i valori compresi (0=privato, 1=pubblico)
    try:
        dati["VIS"] = int(dati["VIS"])
        if dati["VIS"] != 0 and dati["VIS"] != 1:
            raise ValueError
    except ValueError:
        errore = ''

    return errore


# Inserisce un esercizio nella base dati
def inserisci_nuovo_esercizio(dati, creatore, data, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()

    query = "SELECT COUNT(*) FROM ALLENAMENTI"

    try:
        cursor.execute(query)
        # Seleziono il massimo id presente
        if int(list(cursor.fetchone())[0]):
            query = "SELECT MAX(ID) FROM ALLENAMENTI"
            cursor.execute(query)
            val = int(list(cursor.fetchone())[0])+1
        else:
            val = 0
        # Inserisco l'esercizio nella base dati
        query = "INSERT INTO ALLENAMENTI(ID, EMAIL, TITOLO, DESC, LIVELLO, TIPO, DATA) VALUES (?,?,?,?,?,?,?)"

        try:
            cursor.execute(query, (val, creatore, dati["TITOLO"], dati["DESC"], dati["DIFF"],
                                   dati["VIS"], data))
            # Rendo permanenti i cambiamenti
            conn.commit()
            flag = True
        except Exception as e:
            conn.rollback()
            raise e
    except Exception:
        flag = False

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return flag


# Trova tutti gli esercizi pubblici creati
# e anche quelli privati di un dato personal trainer
def trova_tutti_esercizi(personal, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()
    esercizi = list()

    # seleziono tutti gli allenamenti pubblici e quelli privati di un dato personal
    # ordinandoli prima per data decrescente e poi per id decrescente (in caso di parità)
    query = ("SELECT * FROM ALLENAMENTI "
             "WHERE TIPO=? OR EMAIL=?"
             "ORDER BY DATA DESC, ID DESC")
    try:
        # Per ogni
        cursor.execute(query, (1, personal))
        for row in list(cursor.fetchall()):
            esercizi.append({
                "ID": int(row[0]),
                "EMAIL": row[1],
                "TITOLO": row[2],
                "DESC": row[3],
                "DIFF": int(row[4]),
                "VIS": int(row[5]),
                "DATA": row[6],
                "AUTORE": get_dati_utente(row[1], percorso)['NOME'] + " " + get_dati_utente(row[1], percorso)['COGNOME']
            })
    except Exception:
        esercizi = list()

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return esercizi


# Trova tutti i clienti di un dato personal
def trova_clienti_personal(personal, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()
    clienti = list()

    query = "SELECT CLIENTE FROM ASSUNZIONE WHERE ALLENATORE=?"

    # Per ogni cliente ne prendo i dati
    try:
        cursor.execute(query, (personal,))
        for cliente in list(cursor.fetchall()):
            clienti.append(get_dati_utente(cliente[0], percorso))
    except Exception:
        clienti = list()

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return clienti


# Trova tutti gli esercizi creati da un dato personal trainer
def trova_esercizi_personal(personal, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()
    esercizi = list()

    # prendo tutti gli esercizi creati da un personal trainer
    query = ("SELECT * FROM ALLENAMENTI "
             "WHERE EMAIL=?"
             "ORDER BY DATA DESC, ID DESC")
    try:
        cursor.execute(query, (personal,))
        for row in list(cursor.fetchall()):
            esercizi.append({
                "ID": int(row[0]),
                "EMAIL": row[1],
                "TITOLO": row[2],
                "DESC": row[3],
                "DIFF": int(row[4]),
                "VIS": int(row[5]),
                "DATA": row[6]
            })
    except Exception:
        esercizi = list()

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return esercizi


# Trova un singolo esercizio dato il suo id univoco
def get_singolo_esercizio(val, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()

    query = "SELECT * FROM ALLENAMENTI WHERE ID=?"

    # Prendo i dati di un singolo esercizio dato l'id
    try:
        cursor.execute(query, (val,))
        row = list(cursor.fetchone())
        dati = {
                "ID": int(row[0]),
                "EMAIL": row[1],
                "TITOLO": row[2],
                "DESC": row[3],
                "DIFF": int(row[4]),
                "VIS": int(row[5]),
                "DATA": row[6]
            }
    except Exception:
        dati = False

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return dati


# Modifica di un esercizio già inserito
def modifica_esercizio(vecchio, nuovo, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()

    # Aggiorno i campi di un dato allenamento in base all'id
    query = "UPDATE ALLENAMENTI SET TITOLO=?, DESC=?, LIVELLO=?, TIPO=? WHERE ID=? AND EMAIL=?"

    try:
        cursor.execute(query, (nuovo['TITOLO'], nuovo['DESC'], nuovo['DIFF'], nuovo['VIS'],
                               vecchio['ID'], vecchio['EMAIL']))
        # Rendo permanenti i cambiamenti
        conn.commit()
        flag = True
    except Exception:
        conn.rollback()
        flag = False

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return flag


# Inserisci una nuova scheda nella base dati
def inserisci_nuova_scheda(allenatore, cliente, esercizi, percorsi):
    # Connessione alla base dati
    conn = sqlite3.connect(percorsi)
    cursor = conn.cursor()

    # Controllo che ci sia almeno una scheda
    query = "SELECT COUNT(*) FROM SCHEDA"

    try:
        cursor.execute(query)
        if int(list(cursor.fetchone())[0]):
            query = "SELECT MAX(ID) FROM SCHEDA"
            cursor.execute(query)
            val = int(list(cursor.fetchone())[0]) + 1
        else:
            val = 0

        # Inserisco la scheda
        query = ("INSERT INTO SCHEDA(ID, CLIENTE, ALLENATORE, ESERCIZI, RATING) "
                 "VALUES(?,?,?,?,?)")

        # Creo la stringa con tutti gli esercizi
        stringa_esercizi = ''
        for esercizio in esercizi:
            stringa_esercizi = stringa_esercizi + str(esercizio)+","

        cursor.execute(query, (val, cliente, allenatore, stringa_esercizi[0:len(stringa_esercizi)-1:1], -1))
        # Rendo permanenti i cambiamenti
        conn.commit()
        flag = True
    except Exception:
        conn.rollback()
        flag = False

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return flag


# Permette di trovare tutte le schede create da un allenatore
def trova_schede_allenatore(allenatore, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()
    dati = dict()

    query = "SELECT * FROM SCHEDA WHERE ALLENATORE=?"

    # Trovo tutte le schede create da un allenatore
    try:
        cursor.execute(query, (allenatore,))
        for row in list(cursor.fetchall()):
            if row[1] in dati:
                dati[row[1]].append(int(row[0]))
            else:
                dati[row[1]] = [int(row[0])]
    except Exception:
        dati = False

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return dati


# Carica una singola scheda dato id univoco
def get_scheda(val, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()

    # Trovo la scheda dato l'id univoco
    query = "SELECT * FROM SCHEDA WHERE ID=?"
    try:
        cursor.execute(query, (val,))
        row = list(cursor.fetchone())
        dati = {
            "ID": int(row[0]),
            "CLIENTE": row[1],
            "ALLENATORE": row[2],
            "ESERCIZI": row[3].split(","),
            "RATING": row[4]
        }
        esercizi = list()

        # Prendo i dati del cliente
        dati['RICEVENTE'] = get_dati_utente(dati['CLIENTE'], percorso)
        dati['RICEVENTE'] = dati['RICEVENTE']['NOME'] + " " + dati['RICEVENTE']['COGNOME']

        # Prendo i dati dell'allenatore
        dati['AUTORE'] = get_dati_utente(dati['ALLENATORE'], percorso)
        dati['AUTORE'] = dati['AUTORE']['NOME'] + " " + dati['AUTORE']['COGNOME']

        # Prendo i dati di ogni singolo esercizio della scheda
        # e i dati dell'allenatore che ha creato il singolo esercizio
        for id_ese in dati['ESERCIZI']:
            esercizio = get_singolo_esercizio(int(id_ese), percorso)
            esercizio['AUTORE'] = get_dati_utente(esercizio['EMAIL'], percorso)
            esercizio['AUTORE'] = esercizio['AUTORE']['NOME'] + " " + esercizio['AUTORE']['COGNOME']
            esercizi.append(esercizio)
        dati['ESERCIZI'] = esercizi
    except Exception:
        dati = False

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return dati


# Trova tutti gli id delle schede associate a un dato cliente
def trova_schede_cliente(cliente, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()
    val = set()

    query = "SELECT id FROM SCHEDA WHERE CLIENTE=?"

    # Trovo tutti gli id delle schede associate a un cliente
    try:
        cursor.execute(query, (cliente,))
        for row in list(cursor.fetchall()):
            val.add(int(row[0]))
    except Exception:
        val = False

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return val


# Permette di aggiornare la valutazione di una scheda
def valuta_scheda(id_scheda, rating, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()

    query = "UPDATE SCHEDA SET RATING=? WHERE ID=?"

    # Altero il rating di una scheda
    try:
        cursor.execute(query, (rating, id_scheda))
        # Rendo permanenti i cambiamenti
        conn.commit()
        flag = True
    except Exception:
        conn.rollback()
        flag = False

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return flag


# Calcola il ranking di un allenatore data la sua email
def ranking_allenatore(allenatore, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()
    somma = 0
    counter = 0

    # Calcolo il rating di un allenatore solo su rating veri (diversi da -1)
    query = "SELECT RATING FROM SCHEDA WHERE ALLENATORE=? AND RATING<>?"

    try:
        cursor.execute(query, (allenatore, -1))
        # Calcolo la somma di tutti i punteggi delle schede presenti
        for row in list(cursor.fetchall()):
            somma = somma + float(row[0])
            counter = counter + 1
    except Exception:
        counter = -1

    try:
        # Controllo l'assenza di errori
        if counter == -1:
            raise ValueError
        # Cerco nella tabella secondaria (che contiene tutti i rating delle schede eliminate)
        # se è presente l'allenatore in questione
        query = "SELECT RATING FROM RATING WHERE ALLENATORE=?"
        cursor.execute(query, (allenatore,))
        # se si procedo ad aggiungerli alla somma
        dati = list(cursor.fetchone())
        for val in dati[0].split(","):
            counter = counter + 1
            somma = somma + float(val)
    except Exception:
        pass

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    # Controllo che la somma sia valida
    if counter == 0 or counter == -1:
        return -1
    return round(somma/counter, 1)


# Permette di eliminare un esercizio dato il suo id
# l'esercizio non è propriamente eliminato, per evitare di rimuoverlo da schede in cui è presente (cosa da fare
# manualmente modificando la scheda), invece, lo metto come privato (così che non può essere aggiunto o modificato
# dentro una scheda) e lo assegno all'utente anonimo
# idealmente dovrebbe esistere una funzione che fa un controllo periodico per poi eliminare l'esercizio non appena
# non presente in nessuna scheda
def elimina_esercizio(id_esercizio, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()

    # Modifico visibilità ed email
    query = "UPDATE ALLENAMENTI SET TIPO=?, EMAIL=? WHERE ID=?"

    try:
        cursor.execute(query, (0, ANONIMO_EMAIL, id_esercizio))
        # Rendo permanenti i cambiamenti
        conn.commit()
        flag = True
    except Exception:
        conn.rollback()
        flag = False

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return flag


# Permette di eliminare una scheda dato l'id
# eventualmente salvando il rating se non nullo
def elimina_scheda(id_scheda, rating, allenatore, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()

    try:
        # se il rating non è nullo, va salvato
        if rating != -1:
            # Controllo se l'allenatore è già presente nella tabella di salvataggio
            query = "SELECT COUNT(*) FROM RATING WHERE ALLENATORE=?"
            cursor.execute(query, (allenatore,))

            # se si, prelevo i rating presenti, gli concateno quello corrente e lo reinserisco nella base dati
            if int(list(cursor.fetchone())[0]) != 0:
                query = "SELECT RATING FROM RATING WHERE ALLENATORE=?"
                cursor.execute(query, (allenatore,))
                rating = list(cursor.fetchone())[0] + ", " + str(rating)
                query = "UPDATE RATING SET RATING=? WHERE ALLENATORE=?"
                cursor.execute(query, (rating, allenatore))
            else:
                # se no, inserisco direttamente allenatore e rating nella base dati
                query = "INSERT INTO RATING(ALLENATORE, RATING) VALUES (?,?)"
                cursor.execute(query, (allenatore, str(rating)))

        # Cancello la scheda
        query = "DELETE FROM SCHEDA WHERE ID=?"
        cursor.execute(query, (id_scheda,))
        # Rendo permanenti i cambiamenti
        conn.commit()
        flag = True
    except Exception:
        conn.rollback()
        flag = False

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return flag


# Controlla la presenza di un esercizio all'interno della base dati
def controllo_presenza_esercizio(id_es, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()

    query = "SELECT COUNT(*) FROM ALLENAMENTI WHERE ID=?"

    # Controllo che un esercizio sia presente nella base dati
    try:
        cursor.execute(query, (id_es,))
        if int(list(cursor.fetchone())[0]) == 0:
            raise Exception
        flag = True
    except Exception:
        flag = False

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return flag


# Permette di modificare gli esercizi presenti in una scheda
def modifica_scheda(id_scheda, esercizi, percorso):
    # Connessione alla base dati
    conn = sqlite3.connect(percorso)
    cursor = conn.cursor()

    query = "UPDATE SCHEDA SET ESERCIZI=? WHERE ID=?"

    # Inserisco la nuova stringa di esercizi associata alla scheda
    try:
        cursor.execute(query, (esercizi, id_scheda))
        # Rendo permanenti i cambiamenti
        conn.commit()
        flag = True
    except Exception:
        conn.rollback()
        flag = False

    # Chiusura connessione alla base dati
    cursor.close()
    conn.close()
    return flag
