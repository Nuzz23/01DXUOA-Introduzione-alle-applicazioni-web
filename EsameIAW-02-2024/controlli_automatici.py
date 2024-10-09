import dbi_utenti
import dbi_annunci
import dbi_prenotazioni
from werkzeug.security import check_password_hash
from random import randint
import datetime
import dizionario


# Funzione per validare la corretta registrazione di un nuovo utente, in particolare
# non faccio subito return in caso di errore perché voglio segnalare all'utente i campi errati
def valida_nuovo_utente(dati, PERCORSO):
    # Controllo la mail, controllandone la lunghezza, la presenza di . e @ e non di spazi, e che la mail non sia già
    # in uso, tuttavia non comunico se la mail è già in uso o meno in quanto campo potenzialmente sensibile
    # quindi gli errori sul formato e gli errori sulla mail sono trattati allo stesso modo
    risultato = dbi_utenti.check_user_presence_by_email(dati['EMAIL'], PERCORSO)
    if ('.' not in dati['EMAIL'] or '@' not in dati['EMAIL'] or len(dati['EMAIL']) < 8 or len(dati['EMAIL']) > 40
            or ' ' in dati['EMAIL'] or risultato):
        errore = '1'
    else:
        errore = '0'

    # Controllo la password, in particolare mi accerto che siano uguali, la lunghezza sia corretta,
    # sia un minimo forte come password e che non vi siano spazi
    if (dati['PASSWORD'] != dati['PASSWORD2'] or len(dati['PASSWORD']) < 8 or len(dati['PASSWORD']) > 50 or
            ' ' in dati['PASSWORD'] or not (password_forte(dati['PASSWORD']))):
        errore = errore + '1'
    else:
        errore = errore + '0'

    # Controllo il nome scelto, in particolare, siccome il login prevede come identificativo sia mail che password
    # differenzio le due non permettendo la @ nel nome, ovviamente, come con la mail, devo controllare che il nome
    # non sia già in uso, anche qui errori sul formato = errore mail già presente
    risultato = dbi_utenti.check_user_presence_by_name(dati['NOME'], PERCORSO)
    if (not giusti_spazi(dati['NOME']) or not (8 <= len(dati['NOME']) <= 30) or risultato or '@' in dati['NOME']
            or ' ' in dati['NOME']):
        errore = errore + '1'
    else:
        errore = errore + '0'

    # Controllo il telefono scelto, in particolare: se l'utente sceglie un prefisso va bene lo stesso (come evidenziato
    # dalla regex), tuttavia, siccome l'unico prefisso riconosciuto è quello italiano in fase di memorizzazione e
    # controllo sarà opportunamente scartato
    if dati['TELEFONO'].startswith('+') and dati['TELEFONO'][0:3:1] != '+39':
        errore = errore + '1'
        dont_check = True
    elif ' ' in dati['TELEFONO']:
        # mi libero del prefisso e di eventuali spazi
        if dati['TELEFONO'][0:3:1] == '+39':
            telefono = dati['TELEFONO'][0:3:1].split()
        else:
            telefono = dati['TELEFONO'].split()
        dati['TELEFONO'] = ''
        for pezzo in telefono:
            dati['TELEFONO'] = dati['TELEFONO'] + pezzo.strip()
        dont_check = False
    else:
        dont_check = False

    # Controllo la validità di esso (numero su 9 o 10 cifre) e solo numeri
    if not dont_check:
        if len(dati['TELEFONO']) < 9 or len(dati['TELEFONO']) > 10 or not telefono_corretto(dati['TELEFONO']):
            errore = errore + '1'
        else:
            errore = errore + '0'

    try:
        x = int(dati['RUOLO'])
        if x != 0 and x != 1:
            raise ValueError
        errore = errore + '0'
    except ValueError:
        errore = errore + '1'

    return errore


# Mi accerto che la password usata dall'utente sia forte abbastanza
def password_forte(password):
    numero = False
    maiuscola = False
    minuscola = False
    speciale = False

    for carattere in password:
        if 'a' <= carattere <= 'z':
            minuscola = True
        elif 'A' <= carattere <= 'Z':
            maiuscola = True
        elif '0' <= carattere <= '9':
            numero = True
        elif carattere in '#$£%&€*.,-+':
            speciale = True

    if speciale and numero and maiuscola and minuscola:
        return True
    return False


# Controllo che il numero di spazi presenti nella stringa non sia eccessivo
def giusti_spazi(stringa):
    count = 0
    for carattere in stringa:
        if carattere == ' ':
            count = count + 1

    if count >= len(stringa) // 2:
        return False
    return True


# Controllo (sebbene già ci sia la regex) che il telefono sia corretto
def telefono_corretto(telefono):
    try:
        int(telefono)
    except ValueError:
        return False

    return True


# Controllo che la mail fornita sia presente
def controllo_login_mail(email, PERCORSO):
    return dbi_utenti.check_user_presence_by_email(email, PERCORSO)


# Controllo che il nome fornito sia presente
def controllo_login_nome(nome, PERCORSO):
    return dbi_utenti.check_user_presence_by_name(nome, PERCORSO)


# Controllo che la password fornita sia coerente con quella nella base dati
def controllo_login_password(email, password, tipo, PERCORSO):
    pwd = dbi_utenti.get_user_password(email, tipo, PERCORSO)

    # calcolo l'hashing della nuova password e le confronto, se sono uguali bene altrimenti, login failed!
    if check_password_hash(pwd, password):
        return True
    return False


# Controlla la presenza di caratteri non convenzionali in una stringa fornita
def caratteri_strani(stringa):
    for carattere in stringa:
        if ((not 'A' <= carattere.upper() <= 'Z') and (not '0' <= carattere <= '9')
                and carattere not in '#,. _-\'"()[]+/|*!?:'):
            return True
    return False


# Purtroppo non posso creare una funzione che al primo errore torna subito senza controllare gli altri campi
# in quanto voglio segnalare qualsiasi errore sui campi e non fermarmi al primo trovato
def nuovo_annuncio(dati):
    errori = dict()

    try:
        dati['titolo'] = dati['titolo'].strip()
        # Controllo la correttezza del titolo dell'annuncio: lunghezza corretta, non troppi spazi o/e caratteri strani
        if not (10 <= len(dati['titolo']) <= 70) or not giusti_spazi(dati['titolo']) or caratteri_strani(
                dati['titolo']):
            errori['titolo'] = 1
        else:
            errori['titolo'] = 0
    except KeyError or ValueError:
        errori['titolo'] = 1

    # controllo che il civico sia ragionevolmente corretto (no numeri negativi o stupidamente alti)
    # prevedo la possibilità di avere civici non solo numerici es 221B
    # inoltre nel caso in cui il civico sia 0 lo traduco in senza numero
    try:
        # Provo a vedere se è costituito solo da numeri
        errori['civico'] = 0

        try:
            numeri = int(dati['civico'])
            lettere = ''
        except ValueError:
            # se ha anche lettere
            numeri = ''

            # Separo i numeri dalle lettere
            # Nota: ritengo sbagliato un indirizzo del genere 221B2, mentre civici corretti sono 221, 221B, 221/B
            contatore = 0
            while contatore < len(dati['civico']):
                if (dati['civico'][contatore]).isnumeric():
                    numeri += str(dati['civico'][contatore])
                    contatore += 1
                else:
                    break

            # Prendo la parte in lettere
            lettere = (dati['civico'])[contatore::]
            # Facendo da tutor a informatica mi sono accorto di questa cosa buffa --> int('' o ' ') == ValueError
            try:
                numeri = int(numeri)
            except ValueError:
                errori['civico'] = 1

        # Controllo la parte numerica
        if not errori['civico'] and numeri < 0 or int(numeri) > int('9' * 9):
            raise ValueError
        elif numeri == 0:
            numeri = 'SN'

        # Controllo la parte letteraria
        lettere = lettere.upper()
        for lettera in lettere:
            if lettera not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ\\/|- _':
                raise ValueError

        # Unisco le due parti
        dati['civico'] = str(numeri) + lettere

    except ValueError or KeyError or TypeError:
        errori['civico'] = 1

    # Controllo che tipo di strada dell'abitazione sia tra quelli abilitati
    try:
        if dati['tipo_strada'].lower() not in "piazza via viale contrada corso altro":
            errori['tipo_strada'] = 1
        else:
            errori['tipo_strada'] = 0
    except KeyError or ValueError:
        errori['tipo_strada'] = 1

    # Controllo l'indirizzo del locale: la lunghezza e l'uso di caratteri attendibili
    try:
        dati['indirizzo'] = dati['indirizzo'].strip()
        if (not giusti_spazi(dati['indirizzo']) or not (3 <= len(dati['indirizzo']) <= 50)
                or caratteri_strani(dati['indirizzo'])):
            errori['indirizzo'] = 1
        else:
            errori['indirizzo'] = 0
    except KeyError or ValueError:
        errori['indirizzo'] = 1

    # Controllo che il numero di locali fornito sia tra i valori previsti
    try:
        dati['locali'] = int(dati['locali'])
        if not (1 <= dati['locali'] <= 6):
            raise ValueError()
        errori['locali'] = 0
    except ValueError:
        errori['locali'] = 1

    # Controllo la descrizione dell'annuncio
    # Nota: lascio più libertà sui caratteri non applicando la funzione caratteri strani
    # Controllo comunque il numero di spazi
    try:
        dati['descrizione'] = dati['descrizione'].strip()
        if not (giusti_spazi(dati['descrizione'])) or not (30 <= len(dati['descrizione']) <= 700):
            errori['descrizione'] = 1
        else:
            errori['descrizione'] = 0
    except ValueError or KeyError:
        errori['descrizione'] = 1

    # Controllo il prezzo mensile di affitto
    # Nota: il prezzo minimo simbolico è di 0 euro, sotto al quale non si può scendere
    try:
        dati['prezzo'] = int(dati['prezzo'])
        if dati['prezzo'] < 0:
            raise ValueError
        errori['prezzo'] = 0
    except ValueError or KeyError:
        errori['prezzo'] = 1

    # controllo che il tipo di casa sia corretto
    try:
        dati['tipo'] = int(dati['tipo'])
        if 0 <= dati['tipo'] <= 3:
            errori['tipo'] = 0
        else:
            raise ValueError
    except ValueError or KeyError:
        errori['tipo'] = 1

    # Controllo che il campo arredata assuma solo i due valori previsti
    try:
        errori['arredata'] = 0
        # Controllo il campo arredata
        if dati['arredata'] == 'False' or dati['arredata'] == 'True':
            if dati['arredata'] == 'False':
                dati['arredata'] = 0
            else:
                dati['arredata'] = 1
        else:
            raise ValueError
    except ValueError or KeyError:
        errori['arredata'] = 1

    # Controllo che il campo disponibile assuma solo i due valori previsti
    try:
        errori['disponibile'] = 0
        if dati['disponibile'] == 'False' or dati['disponibile'] == 'True':
            if dati['disponibile'] == 'False':
                dati['disponibile'] = 0
            else:
                dati['disponibile'] = 1
        else:
            raise ValueError
    except ValueError or KeyError:
        errori['disponibile'] = 1

    # ritorno i dati elaborati e i potenziali errori su essi
    return [dati, errori]


# Controllo che la foto sia tra i formati da me ritenuti corretti
def controllo_foto_idonea(foto):
    try:
        if foto.strip('.')[-1] not in 'jpeg jpg png heif gif':
            raise IndexError
    except IndexError:
        return False

    return True


# Controllo che due foto dello stesso annuncio non abbiamo nome uguale disgraziatamente
# inoltre randomizzo il nome delle foto così da evitare di avere più foto con lo stesso nome
def foto_nome_uguale(elenco_foto):
    for i in range(len(elenco_foto)):
        # Prendo il tempo e lo inserisco per aggiungere varianza al nome delle foto
        # tolgo eventuali spazi presenti dalla conversione, inoltre aggiungo un numero casuale di caratteri
        # perché le probabilità di avere due foto con lo stesso nome sono basse, ma mai nulle!
        tempo = '_'.join(str(datetime.datetime.now()).replace('.', '_')
                         .replace(':', '_').replace('-', '_').split())
        elenco_foto[i].filename = (elenco_foto[i].filename.split('.')[0] +
                                   tempo + random_char(10) + '.' + elenco_foto[i].filename.split('.')[1])

    return elenco_foto


def random_char(max_char):
    # Scelgo casualmente quanti e quali caratteri inserire
    num_char = randint(1, max_char)
    char = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

    replace = ''
    for i in range(num_char):
        replace = replace + char[randint(0, len(char) - 1)]

    return replace


# differenza tra giorni per vedere che giorno è la prenotazione rispetto l'offset di oggi
def distanza_in_giorni(data1, data2):
    data1 = datetime.datetime.strptime(data1, "%d-%m-%Y")
    data2 = datetime.datetime.strptime(data2, "%d-%m-%Y")
    return abs((data1 - data2).days)


# Gestione delle prenotazioni
def gestisci_prenotazioni(possibili, attive, min_data):
    for prenotazione in attive:
        # azzero la matrice (hash-map 2d?) per le date occupate
        if distanza_in_giorni(min_data, prenotazione[0]) < 7:
            possibili[distanza_in_giorni(prenotazione[0], min_data)][prenotazione[1]] = 0

    return possibili


# Controllo che i dati forniti nel form della nuova prenotazione siano corretti
def controllo_nuova_prenotazione(dati, PERCORSO):
    # Provo ad accedere a cliente
    try:
        dati['cliente'] = dati['cliente'].strip()
    except KeyError or ValueError:
        return False

    # Controllo che il cliente sia presente nella base dati
    if not dbi_utenti.check_user_presence_by_email(dati['cliente'], PERCORSO):
        return False

    # orrore di conversione
    data_min = datetime.date.today() + datetime.timedelta(days=1)
    # Ma perché python lo permette? e perché io lo faccio? Addio leggibilità del codice
    data_max = '-'.join(str(data_min + datetime.timedelta(days=6)).split('-')[::-1])
    data_min = '-'.join(str(data_min).split('-')[::-1])

    # Controllo che la data della prenotazione sia una data sensata
    try:
        dati['data'] = '-'.join(dati['data'].strip().split('-')[::-1])
        if not (datetime.datetime.strptime(data_min, "%d-%m-%Y") <=
                datetime.datetime.strptime(dati['data'], "%d-%m-%Y") <=
                datetime.datetime.strptime(data_max, "%d-%m-%Y")):
            raise ValueError
    except ValueError:
        return False

    # controllo che l'id annuncio sia valido e che l'annuncio sia presente nella base dati
    try:
        dati['id_annuncio'] = int(dati['id_annuncio'])
        if not dbi_annunci.check_annuncio_by_id(dati['id_annuncio'], PERCORSO):
            raise ValueError
    except ValueError:
        return False

    # controllo che la modalità scelta di prenotazione sia corretta
    try:
        dati['tipo'] = int(dati['tipo'])
        if dati['tipo'] != 0 and dati['tipo'] != 1:
            raise ValueError
    except ValueError:
        return False

    # controllo che l'orario scelto sia valido
    try:
        dati['orario'] = int(dati['orario'])
        if not (0 <= dati['orario'] <= 3) or not dbi_prenotazioni.check_orario_prenotazione(dati, PERCORSO):
            raise ValueError
    except ValueError:
        return False

    return dati


# Conta le richieste di prenotazione per tipo (possibili tipi:[Accettata, Rifiutata, In Sospeso])
def conta_richieste(visite):
    pendenti = 0
    accettate = 0
    rifiutate = 0

    for visita in visite:
        if not visita['stato']:
            pendenti += 1
        elif visita['stato'] == 1:
            accettate += 1
        else:
            rifiutate += 1

    return [pendenti, accettate, rifiutate]


# Conto il numero di annunci in base alla disponibilità degli stessi
def conta_annunci(annunci):
    pubblici = 0
    privati = 0

    for annuncio in annunci:
        if annuncio['disponibile']:
            pubblici += 1
        else:
            privati += 1
    return [pubblici, privati]


# Controllo la correttezza dei dati inseriti dopo la modifica di un annuncio già presente
def modifica_annuncio(dati):
    errori = dict()

    # Controllo la correttezza del titolo dell'annuncio
    try:
        dati['titolo'] = dati['titolo'].strip()
        errori['titolo'] = 0
        if not (9 < len(dati['titolo']) <= 70) or not giusti_spazi(dati['titolo']) or caratteri_strani(dati['titolo']):
            raise ValueError
    except KeyError or ValueError:
        errori['titolo'] = 1

    # Controllo il numero di locali
    try:
        dati['locali'] = int(dati['locali'])
        if not (1 <= dati['locali'] <= 6):
            raise ValueError()
        errori['locali'] = 0
    except ValueError:
        errori['locali'] = 1

    # Controllo la descrizione dell'annuncio
    # Nota: lascio più libertà sui caratteri non applicando la funzione caratteri strani
    # Controllo comunque il numero di spazi
    try:
        dati['descrizione'] = dati['descrizione'].strip()
        errori['descrizione'] = 0
        if not (giusti_spazi(dati['descrizione'])) or not (30 <= len(dati['descrizione']) <= 700):
            raise ValueError
    except ValueError or KeyError:
        errori['descrizione'] = 1

    # Controllo il prezzo mensile
    try:
        errori['prezzo'] = 0
        dati['prezzo'] = int(dati['prezzo'])
        if dati['prezzo'] < 0:
            raise ValueError
    except ValueError:
        errori['prezzo'] = 1

    # controllo che il tipo di casa sia corretto
    try:
        errori['tipo'] = 0
        dati['tipo'] = int(dati['tipo'])
        if not (0 <= dati['tipo'] <= 3):
            raise ValueError
    except ValueError or KeyError:
        errori['tipo'] = 1

    # Controllo gli errori su arredata
    try:
        errori['arredata'] = 0
        # Controllo il campo arredata
        if dati['arredata'] == 'False' or dati['arredata'] == 'True':
            if dati['arredata'] == 'False':
                dati['arredata'] = 0
            else:
                dati['arredata'] = 1
        else:
            raise ValueError
    except ValueError or KeyError:
        errori['arredata'] = 1

    # Controllo il campo disponibile
    try:
        errori['disponibile'] = 0
        if dati['disponibile'] == 'False' or dati['disponibile'] == 'True':
            if dati['disponibile'] == 'False':
                dati['disponibile'] = 0
            else:
                dati['disponibile'] = 1
        else:
            raise ValueError
    except ValueError or KeyError:
        errori['disponibile'] = 1

    # ritorno dati puliti ed elaborati ed errori
    return [dati, errori]


# Elabora, pulisce, filtra e unisce le scelte fatte dal locatore su una prenotazione o più
def elabora_prenotazioni(prenotazioni):
    # Definisco tutti i numeri di indici presenti e ne creo una lista di liste con indice-dizionario vuoto
    lista_prenotazioni = list()
    for chiave in prenotazioni:
        chiave = int(chiave.split('-')[1])
        presente = False
        for elemento in lista_prenotazioni:
            if elemento[0] == chiave:
                presente = True
                break
        if not presente:
            lista_prenotazioni.append([chiave, dict()])

    # Per ogni chiave presente, la pulisco dal numero e la assegno all'item corretto
    for chiave in prenotazioni:
        temp = int(chiave.split('-')[1])
        for i in range(len(lista_prenotazioni)):
            if lista_prenotazioni[i][0] == temp:
                (lista_prenotazioni[i][1])[str(chiave.split('-')[0])] = prenotazioni[chiave]
                break

    visite = list()
    # finisco di pulire le prenotazioni ricevute
    for prenotazione in lista_prenotazioni:
        visite.append(prenotazione[1])

    return visite


# Controllo che le scelte fatte dal locatore siano valide e sensate
def valida_scelte_locatore_prenotazioni(prenotazioni, PERCORSO):
    # per ogni prenotazione
    for i in range(0, len(prenotazioni)):
        # Controllo il numero dell annuncio e controllo che esso sia presente
        try:
            prenotazioni[i]['annuncio'] = int(prenotazioni[i]['annuncio'])
            if not dbi_annunci.check_annuncio_by_id(prenotazioni[i]['annuncio'], PERCORSO):
                raise ValueError
        except ValueError or KeyError:
            return []

        # controllo la presenza dell'utente nella base dati
        try:
            if not dbi_utenti.check_user_presence_by_email(prenotazioni[i]['cliente'], PERCORSO):
                raise KeyError
        except KeyError:
            return []

        # Controllo che la data della prenotazione sia una data sensata ed entro i limiti dei 7 giorni
        try:
            data = prenotazioni[i]['data'].split('-')
            # Non c'è limite alla data minima in quanto non stiamo rimuovendo prenotazioni non confermate per date
            # precedenti a quella di oggi

            # Calcolo la data massimo possibile
            data_max = '-'.join(str(datetime.date.today() + datetime.timedelta(days=7)).split('-')[::-1])

            # se la lunghezza della data è diversa da 3 (NO gg-mm-yyyy) o se il giorno/mese/anno non è plausibile
            # siccome il sito è fatto nel 2024 la prima data utile è quella
            if (len(data) != 3 or not dizionario.controlla_data_valida(data[0], data[1], data[2])
                    or datetime.datetime.strptime(prenotazioni[i]['data'], "%d-%m-%Y") >
                    datetime.datetime.strptime(data_max, "%d-%m-%Y")):
                raise ValueError
        except KeyError or ValueError:
            return []

        # controllo che la scelta sia valida
        try:
            prenotazioni[i]['scelta'] = int(prenotazioni[i]['scelta'])
            if prenotazioni[i]['scelta'] != 0 and prenotazioni[i]['scelta'] != 1 and prenotazioni[i]['scelta'] != -1:
                raise ValueError
        except ValueError or KeyError:
            return []

        # controllo che se l'utente ha deciso di rifiutare la prenotazione, sia stata fornita una motivazione
        try:
            if prenotazioni[i]['scelta'] == -1:
                if not (giusti_spazi(prenotazioni[i]['motivo'])) or not (6 <= len(prenotazioni[i]['motivo']) <= 100):
                    raise ValueError
        except ValueError or KeyError:
            return []

    return prenotazioni
