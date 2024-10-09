import sqlite3
import dizionario
from os import remove


# Prendo tutti gli annunci presenti dentro la base dati, secondo un filtro definito
def get_annunci(PERCORSO, filtro):
    conn = sqlite3.connect(PERCORSO)
    cursore = conn.cursor()

    if filtro == 1:       # Prendi tutti gli annunci ordinati per numero di locali e prezzo decrescente
        query = ("SELECT * "
                 "FROM ANNUNCIO "
                 "WHERE ANNUNCIO.DISPONIBILE=? "
                 "ORDER BY ANNUNCIO.LOCALI, ANNUNCIO.PREZZO DESC")
    elif filtro == 2:   # Prendi solo gli annunci di case arredate con prezzi decrescenti
        query = ("SELECT * "
                 "FROM ANNUNCIO "
                 "WHERE ANNUNCIO.DISPONIBILE=? AND ANNUNCIO.ARREDATA=1 "
                 "ORDER BY ANNUNCIO.PREZZO DESC")
    elif filtro == 3:   # Prendi solo gli annunci di case non arredate con prezzi decrescenti
        query = ("SELECT * "
                 "FROM ANNUNCIO "
                 "WHERE ANNUNCIO.DISPONIBILE=? AND ANNUNCIO.ARREDATA=0 "
                 "ORDER BY ANNUNCIO.PREZZO DESC")
    else:       # Prendi tutti gli annunci ordinati per prezzo decrescente (default)
        query = ("SELECT * "
                 "FROM ANNUNCIO "
                 "WHERE ANNUNCIO.DISPONIBILE=? "
                 "ORDER BY ANNUNCIO.PREZZO DESC")

    try:
        cursore.execute(query, (1,))
        risultati = cursore.fetchall()
    except Exception:
        cursore.close()
        conn.close()
        return []

    lista_dati = list()
    query = "SELECT UTENTE.NOME FROM UTENTE WHERE UTENTE.EMAIL=?"
    for risultato in risultati:
        risultato = list(risultato)
        diz = {
            "id": risultato[0],
            "locatore": risultato[1],
            "descrizione": risultato[2],
            "locali": dizionario.traduci_locali(risultato[3], 1),
            "prezzo": risultato[4],
            "tipo": risultato[5],
            "indirizzo": risultato[6],
            "disponibile": risultato[7],
            "titolo": risultato[8],
            "arredata": risultato[9],
            "foto": list()
        }
        cursore.execute(query, (diz['locatore'],))
        try:
            diz['nome_locatore'] = str(list(cursore.fetchone())[0])
        except ValueError or IndexError:
            cursore.close()
            conn.close()
            return []
        lista_dati.append(diz)

    query = ("SELECT FOTOGRAFIA.PATH FROM FOTOGRAFIA "
             "WHERE FOTOGRAFIA.ID = ?")

    try:
        for i in range(len(lista_dati)):
            cursore.execute(query, (lista_dati[i]['id'],))
            for elemento in cursore.fetchall():
                lista_dati[i]['foto'].append(str(elemento).split("\'")[1])
    except Exception:
        cursore.close()
        conn.close()
        return []

    cursore.close()
    conn.close()
    return lista_dati


# Inserisco un nuovo annuncio nella base dati
def inserisci_nuovo_annuncio(dati, PERCORSO_DATABASE, foto, PERCORSO_FOTO):
    conn = sqlite3.connect(PERCORSO_DATABASE)
    cursore = conn.cursor()
    fase = [False, False, False]    # struttura di flag per individuare in caso di errore dove eravamo arrivati

    query = ("SELECT MAX(ANNUNCIO.ID) "
             "FROM ANNUNCIO ")

    # Prendo l'ultimo id usato e lo incremento, se non ne trovo vuol dire che la base dati è vuota e quindi parto da 1
    try:
        cursore.execute(query)
        max_id = int(list(cursore.fetchone())[0]) + 1
    except Exception:
        max_id = 1

    # Devo garantire l'atomicità, o tutto viene salvato correttamente o niente va inserito
    try:
        # Ultimo controllo sul tipo di strada
        if dati['tipo_strada'] == 'Altro':
            dati['tipo_strada'] = ''

        # inserisco l'annuncio
        query = ("INSERT INTO ANNUNCIO "
                 "(ID, LOCATORE, DESCRIZIONE, LOCALI, PREZZO, TIPO, INDIRIZZO, DISPONIBILE, TITOLO, ARREDATA) "
                 "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")

        cursore.execute(query, (max_id, dati['email'], dati['descrizione'], dati['locali'], dati['prezzo'],
                                dati['tipo'], dati['tipo_strada'] + ' ' + dati['indirizzo'] + ', ' + dati['civico'],
                                dati['disponibile'], dati['titolo'], dati['arredata']))
        # Passo la prima fase
        fase[0] = True

        # Provo a salvare le foto nella base dati, se va bene passo alla seconda fase
        for picture in foto:
            picture.save('static/' + PERCORSO_FOTO + picture.filename)

        fase[1] = True

        # Inserisco le foto appena salvate nella base dati, se tutto va bene ho la conferma finale e il commit
        query = "INSERT INTO FOTOGRAFIA(ID, PATH) VALUES(?,?)"
        for immagine in foto:
            cursore.execute(query, (max_id, PERCORSO_FOTO + immagine.filename))
        conn.commit()

        fase[2] = True
    except Exception:
        # Qualcosa va male, faccio il rollback
        conn.rollback()
        cursore.close()
        conn.close()

    # Controllo che l'inserimento sia riuscito, se si bene, altrimenti vedo a che fase si è interrotto
    # Particolarmente critico è il caso in cui si dovesse interrompere tra il salvataggio delle foto e l'inserimento
    # delle foto nella base dati, mi troverei ad avere delle foto che nessun post usa, se così fosse, le rimuovo
    try:
        if not fase[2]:
            if not fase[0]:
                raise ValueError
            if not fase[1]:
                raise ValueError
            else:
                for picture in foto:
                    remove('static/' + PERCORSO_FOTO + picture.filename)
        else:
            # Chiudo la connessione
            cursore.close()
            conn.close()
    except Exception:
        return False

    return True


# Prendo un singolo annuncio identificato dal suo id
def get_annuncio_singolo(PERCORSO_DATABASE, annuncio_id):
    conn = sqlite3.connect(PERCORSO_DATABASE)
    cursore = conn.cursor()

    # Query relativa l'annuncio
    query = "SELECT * FROM ANNUNCIO WHERE ANNUNCIO.ID=? "
    cursore.execute(query, (annuncio_id,))

    # Provo a prendere i parametri dell'annuncio
    try:
        risultato = list(cursore.fetchone())
        annuncio = {
            "id": risultato[0],
            "locatore": risultato[1],
            "descrizione": risultato[2],
            "locali": dizionario.traduci_locali(risultato[3], 1),
            "prezzo": int(risultato[4]),
            "tipo": int(risultato[5]),
            "indirizzo": risultato[6],
            "disponibile": risultato[7],
            "titolo": risultato[8],
            "arredata": risultato[9],
            "foto": list()
        }
    except Exception:
        cursore.close()
        conn.close()
        return []

    # Aggiungo alle informazioni il nome utente, che ho scelto di mostrare rispetto alla mail dello stesso
    query = "SELECT UTENTE.NOME FROM UTENTE WHERE UTENTE.EMAIL=?"
    cursore.execute(query, (annuncio['locatore'],))
    try:
        annuncio['nome_locatore'] = str(list(cursore.fetchone())[0])
    except ValueError or IndexError:
        cursore.close()
        conn.close()
        return []

    # Prendo il percorso relativo alle foto dell'annuncio (tabelle normalizzate)
    query = ("SELECT FOTOGRAFIA.PATH FROM FOTOGRAFIA "
             "WHERE FOTOGRAFIA.ID = ?")

    # provo a prendere ogni foto
    try:
        cursore.execute(query, (annuncio_id,))
        for elemento in cursore.fetchall():
            annuncio['foto'].append(str(elemento).split("\'")[1])
    except Exception:
        cursore.close()
        conn.close()
        return []

    # ritorno l'annuncio correttamente formattato
    cursore.close()
    conn.close()
    return annuncio


# Controllo che un annuncio sia presente nella base dati tramite l'id dello stesso
def check_annuncio_by_id(annuncio, PERCORSO):
    conn = sqlite3.connect(PERCORSO)
    cursore = conn.cursor()

    query = "SELECT COUNT(*) FROM ANNUNCIO WHERE ANNUNCIO.ID=?"

    cursore.execute(query, (annuncio,))

    # provo a estrapolare i risultati della query eseguita in precedenza
    try:
        risultati = cursore.fetchone()
        risultati = int(list(risultati)[0])
    except Exception:
        cursore.close()
        conn.close()
        return False

    cursore.close()
    conn.close()

    if risultati:
        return True
    return False


# Procedo a prendere la mail del locatore che ha creato l'annuncio che si vuole prenotare
def get_locatore_id_by_annuncio(id_annuncio, PERCORSO):
    conn = sqlite3.connect(PERCORSO)
    cursore = conn.cursor()

    # sono sicuro che il locatore è presente nella base dati
    query = "SELECT LOCATORE FROM ANNUNCIO WHERE ANNUNCIO.ID=?"

    cursore.execute(query, (id_annuncio, ))

    try:
        risultato = cursore.fetchone()
        risultato = str(str(risultato).split("'")[1])
    except ValueError:
        cursore.close()
        conn.close()
        return False

    # aggiungo il locatore ai dati
    cursore.close()
    conn.close()
    return risultato


# Integro i dati di una visita con dettagli che permettono una migliora qualità
def integrazione_dati_visita(dati, PERCORSO):
    # prendo i dati del singolo annuncio
    for i in range(0, len(dati)):
        risultato = get_annuncio_singolo(PERCORSO, dati[i]['id_annuncio'])
        dati[i]['indirizzo'] = risultato['indirizzo']
        dati[i]['foto'] = risultato['foto'][0]
        dati[i]['titolo'] = risultato['titolo']
        dati[i]['nome'] = risultato['nome_locatore']
        # traduco i turni di prenotazione
        dati[i]['orario'] = dizionario.traduci_turni(dati[i]['orario'], 1)

    return dati


# Prendo tutti gli annunci, secondo un filtro, di un dato locatore
def get_annunci_by_locatore(locatore, filtro, PERCORSO):
    conn = sqlite3.connect(PERCORSO)
    cursore = conn.cursor()

    if filtro == 1:  # Prendi tutti gli annunci, dal più recente al meno recente (annuncio.id)
        query = ("SELECT * FROM ANNUNCIO "
                 "WHERE ANNUNCIO.LOCATORE = ?"
                 "ORDER BY ANNUNCIO.ID DESC")
        cursore.execute(query, (locatore,))
    elif filtro == 2:   # Prendi tutti gli annunci disponibili, dal più recente al meno recente (annuncio.id)
        query = ("SELECT * FROM ANNUNCIO "
                 "WHERE ANNUNCIO.LOCATORE = ?"
                 "AND ANNUNCIO.DISPONIBILE=?"
                 "ORDER BY ANNUNCIO.ID DESC")
        cursore.execute(query, (locatore, 1))
    else:   # Prendi tutti gli annunci non disponibili, dal più recente al meno recente (annuncio.id)
        query = ("SELECT * FROM ANNUNCIO "
                 "WHERE ANNUNCIO.LOCATORE = ?"
                 "AND ANNUNCIO.DISPONIBILE=?"
                 "ORDER BY ANNUNCIO.ID DESC")
        cursore.execute(query, (locatore, 0))

    risultati = cursore.fetchall()

    lista_dati = list()
    # Pulisci e memorizza gli annunci in una struttura dati adeguata
    try:
        for risultato in risultati:
            risultato = list(risultato)
            diz = {
                "id": risultato[0],
                "descrizione": risultato[2],
                "locali": risultato[3],
                "prezzo": risultato[4],
                "tipo": dizionario.traduci_tipo(risultato[5], 1),
                "indirizzo": risultato[6],
                "disponibile": risultato[7],
                "titolo": risultato[8],
                "arredata": risultato[9],
                "foto": list()
            }
            lista_dati.append(diz)
    except Exception:
        cursore.close()
        conn.close()
        return []

    # Preleva le foto di ogni annuncio
    query = ("SELECT FOTOGRAFIA.PATH FROM FOTOGRAFIA "
             "WHERE FOTOGRAFIA.ID = ?")

    try:
        for i in range(len(lista_dati)):
            cursore.execute(query, (lista_dati[i]['id'],))
            for elemento in cursore.fetchall():
                lista_dati[i]['foto'].append(str(elemento).split("\'")[1])
    except Exception:
        cursore.close()
        conn.close()
        return []

    cursore.close()
    conn.close()
    return lista_dati


# Aggiorno un annuncio già presente nella base di dati
def inserisci_modifica_annuncio(PERCORSO_DB, PATH_FOTO, foto, dati):
    conn = sqlite3.connect(PERCORSO_DB)
    cursore = conn.cursor()
    # Fase di andamento della richiesta
    fase = [False, False, False, False, False, False]
    risultati = False

    # devo garantire la più totale atomicità
    try:
        query = ("UPDATE ANNUNCIO SET DESCRIZIONE=?, LOCALI=?, PREZZO=?, TIPO=?, DISPONIBILE=?, TITOLO=?, ARREDATA=?"
                 "WHERE ANNUNCIO.ID = ? ")

        cursore.execute(query, (dati['descrizione'], dati['locali'], dati['prezzo'], dati['tipo'],
                                dati['disponibile'], dati['titolo'], dati['arredata'], dati['annuncio_id']))
        fase[0] = True   # Fase 1 passata: Update nel database

        # Se ci sono le foto da aggiornare, il discorso si complica, và opportunamente gestita la situazione
        # Devo salvare le foto nuove, cambiare i percorsi delle foto nel database e infine eliminare le foto vecchie
        if foto != -1:
            # Prendo i percorsi alle foto vecchie
            query = "SELECT * FROM FOTOGRAFIA WHERE ID=?"
            cursore.execute(query, (dati['annuncio_id'],))
            risultati = cursore.fetchall()
            fase[1] = True  # Sono riuscito a raggiungere tutte le foto

            query = "DELETE FROM FOTOGRAFIA WHERE FOTOGRAFIA.ID=?"
            cursore.execute(query, (dati['annuncio_id'],))

            fase[2] = True  # Sono riuscito a eliminare correttamente le foto dalla base di dati

            for picture in foto:
                picture.save('static/' + PATH_FOTO + picture.filename)

            fase[3] = True   # Sono riuscito a salvare correttamente le foto in locale

            query = "INSERT INTO FOTOGRAFIA(ID, PATH) VALUES(?,?)"
            for immagine in foto:
                cursore.execute(query, (dati['annuncio_id'], PATH_FOTO + immagine.filename))

            fase[4] = True      # Sono riuscito a inserire correttamente le foto nella base dati
        else:
            fase[5] = True      # ultimo stage vero a priori se non devo modificare le foto

        conn.commit()       # Se tutto è andato a buon fine sino a ora si và col commit
        cursore.close()
        conn.close()
    except Exception:
        conn.rollback()
        cursore.close()
        conn.close()

    try:
        # Se non siamo arrivati alla fase 5 ma abbiamo fatto fino alla fase 4 correttamente
        # e siamo riusciti a salvare i percorsi alle vecchie foto in locale
        # dobbiamo ora rimuoverle, sia per una questione di privacy, sia per evitare spreco di memoria
        if not fase[5] and fase[4] and risultati:
            for risultato in risultati:
                remove('static/' + list(risultato)[1])

            fase[5] = True  # Se siamo riusciti a rimuovere tutte le foto abbiamo finito

        # Se siamo arrivati alla fase finale va tutto bene altrimenti dobbiamo capire dove è andata male
        if not fase[5]:
            # Se è andata male in una delle prime 3 fasi non è un problema, il rollback risolve tutto
            if not fase[0] or not fase[1] or not fase[2]:
                raise ValueError
            # se è andata male la fase 4, dobbiamo togliere le foto salvate in locale prima di poter comunicare l'errore
            elif fase[3]:
                for picture in foto:
                    remove('static/' + PATH_FOTO + picture.filename)
    except Exception:
        return False

    return True


# Quando visualizzo un annuncio singolo prendo i consigliati sulla base dello stesso
def get_consigliati(base, PERCORSO):
    conn = sqlite3.connect(PERCORSO)
    cursore = conn.cursor()
    # Imposto una prima soglia sula differenza di prezzo e una seconda sulla differenza di locali
    soglia_prezzo = 250
    soglia_locali = 1
    consigliati = list()

    # Ringraziamo Danilo per basi di dati
    query = ("SELECT * "
             "FROM ANNUNCIO AS A1 "
             "WHERE A1.ID!=? AND A1.DISPONIBILE=? AND A1.ID IN ("
                "SELECT DISTINCT A2.ID "
                "FROM ANNUNCIO AS A2 "
                "WHERE ABS(A2.PREZZO-?) <= ? OR ABS(A2.LOCALI-?) <= ? or A2.TIPO=? "
                "AND A2.DISPONIBILE=?"
             ")")

    # proviamo a eseguire la query e a costruire la lista di dizionari per gestire i risultati
    try:
        cursore.execute(query, (base['id'], 1, base['prezzo'], soglia_prezzo, base['locali'], soglia_locali,
                                base['tipo'], 1))
        risultati = cursore.fetchall()
        for risultato in risultati:
            risultato = list(risultato)
            diz = {
                "id": risultato[0],
                "locatore": risultato[1],
                "descrizione": risultato[2],
                "locali": risultato[3],
                "prezzo": risultato[4],
                "tipo": risultato[5],
                "indirizzo": risultato[6],
                "disponibile": risultato[7],
                "titolo": risultato[8],
                "arredata": risultato[9],
                "foto": list()
            }

            # di ogni risultato prendo la prima foto per fare da copertina del consigliato
            query = "SELECT F.PATH FROM FOTOGRAFIA AS F WHERE F.ID=?"
            cursore.execute(query, (diz['id'],))
            risultato = cursore.fetchone()
            diz['foto'].append(str(list(risultato)[0]))
            consigliati.append(diz)
    except Exception:
        cursore.close()
        conn.close()
        return []

    # ritorno la struttura dati
    cursore.close()
    conn.close()
    return consigliati
