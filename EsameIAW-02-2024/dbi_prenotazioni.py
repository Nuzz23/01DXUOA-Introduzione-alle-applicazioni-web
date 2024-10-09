import datetime
import sqlite3
import dizionario
import controlli_automatici


# Prendo tutte le prenotazioni relative a un determinato annuncio entro una determinata data
def get_prenotazioni(PERCORSO, annuncio_id):
    conn = sqlite3.connect(PERCORSO)
    cursor = conn.cursor()

    # non faccio prenotare da oggi ma da domani per dare tempo al locatore di visualizzare le richieste e decidere
    data_min = datetime.date.today() + datetime.timedelta(days=1)
    # Ma perché python lo permette? e perché io lo faccio?
    data_max = '-'.join(str(data_min + datetime.timedelta(days=6)).split('-')[::-1])
    data_min = '-'.join(str(data_min).split('-')[::-1])

    # Non uso la data max nella query perché sò che massimo potrò prenotare fino a otto giorni da oggi, escluso oggi
    # quindi sicuro non ci sono date oltre il max
    query = ("SELECT DATA, ORARIO, TIPO "
             "FROM VISITA "
             "WHERE VISITA.ID_ANNUNCIO=? "
             "AND  VISITA.DATA >= ? AND (VISITA.STATO = ? OR VISITA.STATO = ?)"
             "ORDER BY DATA")
    cursor.execute(query, (annuncio_id,  data_min, 1, 0))

    # Provo a prendere le prenotazioni
    try:
        risultati = cursor.fetchall()
    except Exception:
        risultati = -1

    cursor.close()
    conn.close()

    # le filtro adeguatamente (solo valide o in sospeso) e le memorizzo
    prenotazioni = list()
    try:
        if risultati != -1:
            for risultato in risultati:
                risultato = list(risultato)
                if int(risultato[2]) == 1 or not int(risultato[2]):
                    prenotazioni.append([risultato[0], risultato[1]])
        else:
            raise ValueError
    except ValueError:
        return -1

    # Creo la matrice che gestisce le prenotazioni, inizialmente tutta libera
    possibili = dizionario.crea_prenotazioni()

    # Inizio a togliere i posti già prenotati tra tutti quelli possibili
    prenotazioni = controlli_automatici.gestisci_prenotazioni(possibili, prenotazioni, data_min)

    # se c'è almeno un posto libero ritorno le prenotazioni, la data min e la data max
    for giorno in prenotazioni:
        for orario in giorno:
            if orario:
                return ['-'.join(data_min.split('-')[::-1]), '-'.join(data_max.split('-')[::-1]), prenotazioni]

    return []


# Posso controllare le prenotazioni a un dato annuncio, per un dato utente, in particolare
# usando un flag posso controllare tutte le prenotazioni(0) o solo quelle attive(1)
def check_prenotazioni(PERCORSO, annuncio_id, utente_id, filtro):
    conn = sqlite3.connect(PERCORSO)
    cursor = conn.cursor()

    # differenzio le due potenziali query
    if not filtro:
        query = ("SELECT COUNT(*) FROM VISITA "
                 "WHERE VISITA.ID_ANNUNCIO=? AND VISITA.CLIENTE=?")
        cursor.execute(query, (annuncio_id, utente_id))
    else:
        query = ("SELECT COUNT(*) FROM VISITA WHERE VISITA.ID_ANNUNCIO=? "
                 "AND (VISITA.STATO =? OR VISITA.STATO=?) AND VISITA.CLIENTE=?")
        cursor.execute(query, (annuncio_id, 0, 1, utente_id))

    # eseguo la query
    try:
        risultati = cursor.fetchone()
        risultati = int(list(risultati)[0])
    except Exception:
        risultati = 1

    cursor.close()
    conn.close()
    return risultati


def check_orario_prenotazione(dati, PERCORSO):
    conn = sqlite3.connect(PERCORSO)
    cursor = conn.cursor()

    query = ("SELECT COUNT(*) "
             "FROM VISITA "
             "WHERE VISITA.ID_ANNUNCIO=? AND VISITA.DATA = ? "
             "AND VISITA.ORARIO = ? AND (VISITA.STATO=? OR VISITA.STATO=?)")

    cursor.execute(query, (dati['id_annuncio'], dati['data'], dati['orario'], 0, 1))

    try:
        risultati = cursor.fetchone()
        risultati = int(list(risultati)[0])
        if risultati:
            raise ValueError
    except ValueError:
        cursor.close()
        conn.close()
        return 0

    cursor.close()
    conn.close()

    if not risultati:
        return 1
    return 0


# inserisco una nuova prenotazione valida per una visita
def aggiungi_nuova_prenotazione(dati, PERCORSO):
    conn = sqlite3.connect(PERCORSO)
    cursor = conn.cursor()

    # Prendo l'ultimo numero progressivo di prenotazione per quel determinato utente per quella determinata data
    # e per quel determinato annuncio (altrimenti anche se un locatore rifiutasse una richiesta il cliente non
    # potrebbe prenotare di nuovo per la stessa data)
    query = ("SELECT MAX(PROGRESSIVO) FROM VISITA "
             "WHERE VISITA.ID_ANNUNCIO=? AND VISITA.DATA =? AND VISITA.LOCATORE =?")

    # Se non si trova il progressivo è perché non c'è quindi lo inizializzo io a 0
    try:
        cursor.execute(query, (dati['id_annuncio'], dati['data'], dati['locatore']))
        max_progressivo = int(list(cursor.fetchone())[0])+1
    except Exception:
        max_progressivo = 0

    # ricontrollo che lo slot sia libero un'ultima volte sebbene già fatto prima
    if not check_slot_libero(PERCORSO, dati):
        cursor.close()
        conn.close()
        return False

    # Provo a inserire la prenotazione ora che ho tutte le informazioni che mi servono
    query = ("INSERT INTO VISITA(CLIENTE, LOCATORE, ID_ANNUNCIO, DATA, TIPO, ORARIO, STATO, PROGRESSIVO) "
             "VALUES (?,?,?,?,?,?,?,?)")

    try:
        cursor.execute(query, (dati['cliente'], dati['locatore'], dati['id_annuncio'], dati['data'],
                               dati['tipo'], dati['orario'], 0, max_progressivo))
        conn.commit()
    except Exception:
        conn.rollback()
        cursor.close()
        conn.close()
        return False

    cursor.close()
    conn.close()
    return True


# Prendo le prenotazioni ordinate per data di un dato utente secondo quanto indicato da un filtro
def get_prenotazioni_by_cliente(cliente, filtro, PERCORSO):
    conn = sqlite3.connect(PERCORSO)
    cursor = conn.cursor()

    if filtro == 1:         # Filtro qualsiasi prenotazione (default)
        query = ("SELECT * FROM VISITA WHERE VISITA.CLIENTE = ? "
                 "ORDER BY visita.data desc, VISITA.ORARIO DESC, PROGRESSIVO DESC")
        cursor.execute(query, (cliente, ))
    elif filtro == 2:       # Filtro solo le prenotazioni confermate
        query = ("SELECT * FROM VISITA "
                 "WHERE VISITA.CLIENTE = ? AND VISITA.STATO=? "
                 "order by visita.data desc, visita.orario desc, PROGRESSIVO DESC")
        cursor.execute(query, (cliente, 1, ))
    elif filtro == 3:         # Filtro solo le prenotazioni rifiutate
        query = ("SELECT * FROM VISITA "
                 "WHERE VISITA.CLIENTE = ? AND VISITA.STATO=? "
                 "order by visita.data desc, visita.orario desc, PROGRESSIVO DESC")
        cursor.execute(query, (cliente, -1))
    else:  # Filtro solo le prenotazioni non confermate
        query = ("SELECT * FROM VISITA "
                 "WHERE VISITA.CLIENTE = ? AND VISITA.STATO=? "
                 "order by visita.data desc, visita.orario desc, PROGRESSIVO DESC")
        cursor.execute(query, (cliente, 0))

    # prenderò i risultati indipendentemente dal filtro applicato
    risultati = cursor.fetchall()
    cursor.close()
    conn.close()

    lista_prenotazioni = list()
    try:
        # Pulisco i risultati e li metto dentro una lista
        for risultato in risultati:
            risultato = list(risultato)
            diz = {
                'locatore': risultato[1],
                'id_annuncio': int(risultato[2]),
                'data': risultato[3],
                'tipo': int(risultato[4]),
                'orario': int(risultato[5]),
                'stato': int(risultato[6]),
                'motivo': risultato[7]
            }
            lista_prenotazioni.append(diz)
    except Exception:
        return False

    return lista_prenotazioni


# Prendo tutte le prenotazioni ricevute da un dato locatore
def get_prenotazioni_by_locatore(locatore, PERCORSO):
    conn = sqlite3.connect(PERCORSO)
    cursor = conn.cursor()

    # Non serve fare il controllo in quanto dati già in tabella
    query = ("SELECT * "
             "FROM VISITA AS V, UTENTE AS U, ANNUNCIO AS A "
             "WHERE V.LOCATORE = ? AND V.CLIENTE=U.EMAIL AND A.ID=V.ID_ANNUNCIO "
             "ORDER BY DATE(V.DATA)")
    cursor.execute(query, (locatore, ))

    risultati = cursor.fetchall()
    cursor.close()
    conn.close()

    # Memorizzo le informazioni in una opportuna struttura dati
    lista_prenotazioni = list()
    try:
        for risultato in risultati:
            risultato = list(risultato)
            diz = {
                'cliente': risultato[0],
                'id_annuncio': int(risultato[2]),
                'data': risultato[3],
                'tipo': int(risultato[4]),
                'orario': dizionario.traduci_turni(int(risultato[5]), 1),
                'stato': int(risultato[6]),
                'motivo': risultato[7],
                'cliente_nome': risultato[13],
                'titolo': risultato[22],
                'indirizzo': risultato[20],
                'progressivo': risultato[8]
            }
            lista_prenotazioni.append(diz)
    except Exception:
        return False

    # ordino le prenotazioni per data e per turno
    lista_prenotazioni = dizionario.quick_sort(lista_prenotazioni)

    return lista_prenotazioni


# Controllo che lo slot scelto dall'utente sia ancora libero per un dato annuncio
def check_slot_libero(PERCORSO, dati):
    conn = sqlite3.connect(PERCORSO)
    cursor = conn.cursor()

    # provo a eseguire la query, nota per libero si intende slot che non presenta prenotazioni in sospeso o accettate
    # sono invece valide un numero di prenotazioni rifiutate potenzialmente infinite per quello slot
    query = ("SELECT COUNT(*) FROM VISITA "
             "WHERE ID_ANNUNCIO=? AND DATA=? AND ORARIO=?"
             "AND (STATO =? OR STATO =?)")

    cursor.execute(query, (dati['id_annuncio'], dati['data'], dati['orario'], 1, 0))
    try:
        risultato = cursor.fetchone()
        risultato = int(list(risultato)[0])
    except Exception:
        cursor.close()
        conn.close()
        return False

    cursor.close()
    conn.close()

    if risultato:
        return False
    return True


# Aggiorna le prenotazioni di un dato locatore
def aggiorna_prenotazioni(lista_prenotazioni, locatore, PERCORSO):
    conn = sqlite3.connect(PERCORSO)
    cursor = conn.cursor()

    # a seconda del tipo di prenotazione dovrò modificare solo il campo stato (accetta)
    # o il campo stato e il campo motivo (solo rifiuto)
    query_accetta_posponi = ("UPDATE VISITA SET STATO=? WHERE ID_ANNUNCIO=? AND DATA=? AND CLIENTE=? AND LOCATORE=? "
                             "AND PROGRESSIVO=?")
    query_rifiuta = ("UPDATE VISITA SET STATO=?, MOTIVO=? WHERE ID_ANNUNCIO=? AND DATA=? AND CLIENTE=? "
                     "AND LOCATORE=? AND PROGRESSIVO=?")

    try:
        # Prendo il massimo numero progressivo per quella data, cliente e annuncio, in quanto se stiamo modificando
        # solo prenotazioni in sospeso e il cliente non può avere più di una prenotazione in sospeso per annuncio
        # l'ultima avrà sicuramente il campo progressivo massimo

        query = 'SELECT MAX(PROGRESSIVO) FROM VISITA WHERE ID_ANNUNCIO=? AND DATA=? AND CLIENTE=? AND LOCATORE=?'
        for prenotazione in lista_prenotazioni:
            # Ha senso solo modificare prenotazioni accettate o rifiutate
            if prenotazione['scelta']:
                cursor.execute(query, (prenotazione['annuncio'], prenotazione['data'],
                                       prenotazione['cliente'], locatore))

                # non serve gestire il caso in cui non si trovi, in quanto è sicuramente presente la prenotazione
                max_prenotazione = int(list(cursor.fetchone())[0])

                # a seconda della scelta scelgo quale query eseguire
                if prenotazione['scelta'] == -1:
                    cursor.execute(query_rifiuta, (prenotazione['scelta'], prenotazione['motivo'],
                                                   prenotazione['annuncio'], prenotazione['data'],
                                                   prenotazione['cliente'], locatore, max_prenotazione))
                else:
                    cursor.execute(query_accetta_posponi, (prenotazione['scelta'], prenotazione['annuncio'],
                                                           prenotazione['data'], prenotazione['cliente'],
                                                           locatore, max_prenotazione))
        # Due diverse filosofie: fare il commit una volta per ogni iterazione o solo a fine ciclo?
        # Personalmente io preferisco a fine ciclo per garantire l'atomicità della scelta, poi cambia poco
        conn.commit()
        stato = True
    except Exception:
        conn.rollback()
        stato = False

    cursor.close()
    conn.close()
    return stato
