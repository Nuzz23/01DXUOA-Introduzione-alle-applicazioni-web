# Lasciate ogni speranza di trovare codice leggibile voi ch'entrate, dai mi sono impegnato per migliorarlo ;)
# Librerie necessarie
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash

# Librerie per la gestione dell'utente
from models import User

# Librerie per la gestione dei database
import dbi_utenti  # Funzioni legate all'utente
import dbi_annunci  # Funzioni legate agli annunci
import dbi_prenotazioni  # Funzioni legate alle prenotazioni degli annunci

# Librerie per i controlli per evitare che l'utente faccia il furbetto
import controlli_automatici

# Librerie per le traslazioni database(computerese)-italiano e viceversa
import dizionario

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'OSCILLOSCOPIO ANALOGICO-DIGITALE DA BANCO RIGOL DS1054Z'

# PERCORSI COSTANTI
PERCORSO_DATABASE = "base_di_dati/base_dati.db"  # Path per il Database
PERCORSO_FOTO = 'img/case/'  # Path per le foto


# ------------------------   PARTE RIGUARDANTE LA SCHERMATA DI HOME DEL SITO  ----------------------------------------

# Gestisco la home page del sito
@app.route('/')
def home():
    # Prendo gli annunci presenti nella base di dati, lo zero indica un valore di default,
    # ovvero, applico il filtro di default (ordinamento per prezzo decrescente)
    annunci = dbi_annunci.get_annunci(PERCORSO_DATABASE, 0)
    num_annunci = len(annunci)

    # Controllo se l'utente ha fatto o meno il login, se sì ne passo i dati per l'header e anche per capire il tipo
    # di permessi concessi all'utente, altrimenti, passo un placeholder per la variabile utente
    if current_user.is_authenticated:
        utente = current_user
    else:
        utente = ''

    # Renderizzo il template della home
    return render_template('home.html', annunci=annunci, utente=utente, num_annunci=num_annunci)


# Gestisco la home in versione filtrata, per permettere all'utente di vedere solo alcuni annunci
@app.route('/home_filtered/<int:id_filtro>')
def home_filtered(id_filtro):
    # Prendo gli annunci presenti nel database secondo il filtro scelto dall'utente
    annunci = dbi_annunci.get_annunci(PERCORSO_DATABASE, id_filtro)
    num_annunci = len(annunci)

    # Controllo se l'utente ha fatto o meno il login, se sì ne passo i dati per l'header e anche per capire il tipo
    # di permessi concessi all'utente, altrimenti, passo un placeholder per la variabile utente
    if current_user.is_authenticated:
        utente = current_user
    else:
        utente = ''

    # Sebbene sia la home filtrata il template a cui riporto è sempre la home classica
    return render_template('home.html', annunci=annunci, utente=utente, num_annunci=num_annunci)


# ------------------  PARTE RIGUARDANTE IL LOGIN DELL'UTENTE PRECEDENTEMENTE REGISTRATO  ----------------------------

# Reindirizzo alla pagina di login, svolgo un controllo sugli errori in caso di login non andato a buon fine
@app.route('/login/<int:errore>')
def login(errore):
    return render_template('login.html', errore=errore)


# Mi occupo del login di un'utente
@app.route('/login_success', methods=['POST'])
def login_success():
    # Controllo il metodo usato nel form (mi assicuro sia HTTP POST) [qui usiamo solo le POST, non le GET nei form]
    if request.method == 'POST':
        # Prendo i dati del login dal form
        dati = request.form.to_dict()

        # Provo a elaborare i dati del form, in caso di errore, rimando al login segnalandolo
        try:
            username = dati['EMAIL'].strip()
            password = dati['PASSWORD'].strip()
        except KeyError or ValueError:
            return redirect(url_for('login', errore=True))

        # Permetto una doppia modalità di login, per email o per nome utente, in quanto, sebbene la email sia la
        # chiave prima della tabella utente nella base di dati, il campo nome è unique not null, quindi una ottima
        # chiave candidata per sostituire la mail. A distinguere i due sarà la @,
        # che NON può essere inserita in un nome utente, ma è necessariamente presente nella mail
        # Login per email: controllo presenza utente nella base dati
        if '@' in username:
            if not controlli_automatici.controllo_login_mail(username, PERCORSO_DATABASE):
                app.logger.error('Username o/e password non valide')
                return redirect(url_for('login', errore=True))
        else:
            # Login per nome: controllo presenza utente nella base dati
            if not controlli_automatici.controllo_login_nome(username, PERCORSO_DATABASE):
                app.logger.error('Username o/e password non valide')
                return redirect(url_for('login', errore=True))

        # controllo della correttezza della password, uso questa espressione brutta per definire il tipo di login
        if not controlli_automatici.controllo_login_password(username, password, '@' in dati['EMAIL'],
                                                             PERCORSO_DATABASE):
            app.logger.error('Mail o/e password non valide')
            return redirect(url_for('login', errore=True))

        # Prendo gli altri dati dell'utente per il login, a seconda del modo, dovrò trovare l'utente in maniera diversa
        if '@' in username:
            dati = dbi_utenti.get_user_by_email(username, PERCORSO_DATABASE)
        else:
            dati = dbi_utenti.get_user_by_name(username, PERCORSO_DATABASE)

        # controllo che non ci sia stato qualche errore nel trovare l'utente
        if not dati:
            app.logger.error('Mail o/e password non valide')
            return redirect(url_for('login', errore=True))

        # eseguo il login dell'utente
        dati = User(email=dati['EMAIL'], password=dati['PASSWORD'], telefono=dati['TELEFONO'],
                    ruolo=dati['RUOLO'], nome=dati['NOME'])
        login_user(dati, True)

        # porto alla schermata home dopo un login corretto
        return redirect(url_for('home'))
    else:
        app.logger.error('Metodo non corretto')
        return redirect(url_for('home'))


# Classico user loader, non ci spenderei molto
@login_manager.user_loader
def load_user(user_id):
    # Sfrutta la funzione che permette di caricare i dati dell'utente tramite mail
    db_user = dbi_utenti.get_user_by_email(user_id, PERCORSO_DATABASE)

    user = User(email=db_user['EMAIL'], nome=db_user['NOME'], password=db_user['PASSWORD'], ruolo=db_user['RUOLO'],
                telefono=db_user['TELEFONO'])

    return user


# Classico logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# -------------------------------   PARTE DI REGISTRAZIONE DELL'UTENTE   ----------------------------------------------

# Funzione che permette di gestire la prima parte della registrazione, ovvero il form ed errori su esso
@app.route('/register/<string:okay>')
def register(okay):
    # Traduco gli errori da stringa numerica a singolo errore per campo

    return render_template('register.html', errore=dizionario.traduci_errore(okay, 1),
                           campi=dizionario.crea_dizionario_registrazione_vuoto())


# Mi occupo della registrazione di un utente indipendentemente che sia un locatore o un cliente
# In questo caso il form è gia stato compilato, bisogna validare i dati
@app.route('/register_success', methods=['POST'])
def register_success():
    # Riprendo i dati e controllo la loro correttezza
    dati = request.form.to_dict()
    try:
        dati['TELEFONO'] = dati['TELEFONO'].strip()
    except KeyError or ValueError:
        app.logger.error('Telefono non valido! ')
        return render_template(url_for('register', okay='00010'))

    # Controllo la correttezza dei dati forniti con flag multipli
    risposta = controlli_automatici.valida_nuovo_utente(dati, PERCORSO_DATABASE)

    # se tutti i controlli sono passati posso pensare di inserire l'utente nella base dati
    if '1' not in risposta:
        # Creo una l'hash della password, lo inserisco nella base dati e ne faccio il login in automatico
        # Così non deve poi di nuovo fare il login
        dati['PASSWORD'] = generate_password_hash(dati['PASSWORD'])
        if dbi_utenti.registra_nuovo_utente(dati, PERCORSO_DATABASE):
            dati = User(email=dati['EMAIL'], password=dati['PASSWORD'], telefono=dati['TELEFONO'], ruolo=dati['RUOLO'],
                        nome=dati['NOME'])
            login_user(dati, True)
            return redirect(url_for('home'))
        else:
            # se non va l'inserimento si comunica e si riprova, cercando di salvare i campi già validi
            app.logger.error('Registrazione non riuscita')
            campi = dizionario.crea_dizionario_registrazione_vuoto()
            if not int(risposta[2]):
                campi['nome'] = str(dati['NOME'])
            if not int(risposta[0]):
                campi['email'] = str(dati['EMAIL'])
            if not int(risposta[3]):
                campi['telefono'] = str(dati['TELEFONO'])
            try:
                if not int(risposta[4]):
                    campi['ruolo'] = int(dati['RUOLO'])
                else:
                    raise ValueError
            except ValueError:
                campi['ruolo'] = 3

            return render_template('register.html',
                                   errore=dizionario.traduci_errore(risposta, 1), campi=campi)
    else:
        # se non va l'inserimento si comunica e si riprova, cercando di salvare i campi già validi
        app.logger.error('Errori nei campi forniti')
        campi = dizionario.crea_dizionario_registrazione_vuoto()
        if not int(risposta[2]):
            campi['nome'] = str(dati['NOME'])
        if not int(risposta[0]):
            campi['email'] = str(dati['EMAIL'])
        if not int(risposta[3]):
            campi['telefono'] = str(dati['TELEFONO'])
        try:
            if not int(risposta[4]):
                campi['ruolo'] = int(dati['RUOLO'])
            else:
                raise ValueError
        except ValueError:
            campi['ruolo'] = 3

        return render_template('register.html',
                               errore=dizionario.traduci_errore(risposta, 1), campi=campi)


# -------------------------     GESTIONE ANNUNCI -> CREAZIONE NUOVO ANNUNCIO     ---------------------------------


# Permetto la creazione di un nuovo annuncio, solo per locatori registrati
@app.route('/nuovo_annuncio')
@login_required
def nuovo_annuncio():
    # Controllo che l'utente sia registrato come locatore, se si può compilare il form, altrimenti va al login
    if current_user.is_authenticated and current_user.RUOLO:
        return render_template('nuovo_annuncio.html', utente=current_user, dati='',
                               errori=dizionario.crea_errori_corretto())
    else:
        app.logger.error('Utente non registrato o ruolo utente non adeguato')
        return redirect(url_for('login', errore=False))


@app.route('/nuovo_annuncio_successo', methods=['POST'])
@login_required
def nuovo_annuncio_successo():
    # Controllo che la richiesta sia arrivata correttamente, che l'utente sia loggato con i permessi corretti
    if request.method == "POST" and current_user.is_authenticated and current_user.RUOLO:

        dati = request.form.to_dict()
        # Controllo che l'utente che ha compilato il form sia effettivamente presente nella base dati
        # e controllo che i sue id coincidano
        if (not dbi_utenti.check_user_presence_by_email(dati['email'], PERCORSO_DATABASE)
                or dati['email'] != current_user.id):
            app.logger.error('Utente non trovato nella base dati')
            return render_template('nuovo_annuncio.html', utente=current_user, dati='',
                                   errori=dizionario.crea_errori_corretto())

        # Controllo la correttezza dei dati e li elaboro parzialmente
        risposta = controlli_automatici.nuovo_annuncio(dati)

        # Salvo i dati ottenuti
        dati = risposta[0]
        errori = risposta[1]

        foto = request.files.getlist('foto')

        # Controllo le foto caricate
        errori['foto'] = 0
        # Controllo le foto
        foto = controlli_automatici.foto_nome_uguale(foto)
        conta = 0
        for picture in foto:
            if not controlli_automatici.controllo_foto_idonea(picture.filename):
                errori['foto'] = 1
                break
            else:
                conta = conta + 1

        # Conto il numero effettivo di foto fornite
        if conta < 1 or conta > 5:
            errori['foto'] = 1

        # Controllo la presenza di errori
        errore = 0
        for valore in errori:
            if errori[valore]:
                errore = 1
                break

        # Se non ci sono errori provo a inserire i dati nella base dati, altrimenti ritorno all'inserimento
        if not errore:
            if dbi_annunci.inserisci_nuovo_annuncio(dati, PERCORSO_DATABASE, foto, PERCORSO_FOTO):
                return redirect(url_for('home'))
            else:
                # Permetto di salvare i campi corretti per non farli reinserire all'utente (tutti se siamo arrivati qui)
                riporta = dict()
                for chiave in errori:
                    if not errori[chiave] and chiave != 'foto':
                        riporta[chiave] = dati[chiave]

                app.logger.error('Errore lato server durante l\'inserimento del nuovo post')
                return render_template('nuovo_annuncio.html',
                                       dati=riporta, errori=errori, utente=current_user)
        else:
            # Permetto di salvare i campi corretti per non farli reinserire all'utente
            riporta = dict()
            for chiave in errori:
                if not errori[chiave] and chiave != 'foto':
                    riporta[chiave] = dati[chiave]

            app.logger.error('Errore')
            return render_template('nuovo_annuncio.html',
                                   utente=current_user, errori=errori, dati=riporta)
    else:
        app.logger.error('metodo richiesta non valido')
        return render_template('nuovo_annuncio.html', utente=current_user,
                               errori=dizionario.crea_errori_corretto(), dati='')


#   --------------------------------    VISUALIZZAZIONE CORRETTA DELL'ANNUNCIO    -------------------------------------

@app.route('/annuncio/<int:annuncio_id>')
def annuncio(annuncio_id):
    # Prendo le informazioni dell'annuncio che l'utente vorrebbe visualizzare
    annuncio_info = dbi_annunci.get_annuncio_singolo(PERCORSO_DATABASE, annuncio_id)

    # L'annuncio può essere visualizzato se è solo se:
    # é disponibile (quindi visibile sulla home)
    # Sono il locatore che lo ha creato
    # Ho una prenotazione valida (indipendentemente dallo stato) per quell'annuncio (indipendentemente dalla data)
    if annuncio_info['disponibile'] or (not annuncio_info['disponibile'] and current_user.is_authenticated and
                (dbi_prenotazioni.check_prenotazioni(PERCORSO_DATABASE, annuncio_id, current_user.id, 0)
                or current_user.id == annuncio_info['locatore'])):

        # Inizializzo le variabili data
        data_min = ''
        data_max = ''

        # Controllo che l'utente sia autenticato, non sia il creatore dell'annuncio e non abbia prenotazioni in
        # sospeso o confermato per esse, se si a tutte e tre le domande, abilito la possibilità di prenotare una visita
        if (current_user.is_authenticated and current_user.id != annuncio_info['locatore'] and
                not dbi_prenotazioni.check_prenotazioni(PERCORSO_DATABASE, annuncio_id, current_user.id, 1)):

            # Prendo le prenotazioni
            prenotazioni = dbi_prenotazioni.get_prenotazioni(PERCORSO_DATABASE, annuncio_id)

            # Stato prenotazioni già piene
            if not prenotazioni or prenotazioni == -1:
                prenotazioni = 3
            else:
                # Possibile prenotare
                data_min = prenotazioni[0]
                data_max = prenotazioni[1]
                prenotazioni = prenotazioni[2]
        # Status personalizzato in base al motivo per il quale l'utente non può prenotare
        elif not current_user.is_authenticated:
            prenotazioni = 0
        elif current_user.id == annuncio_info['locatore']:
            prenotazioni = 1
        else:
            prenotazioni = 2

        if current_user.is_authenticated:
            utente = current_user
        else:
            utente = ''

        # Traduco il tipo di immobile da numero a un formato human-readable
        annuncio_info['tipo'] = dizionario.traduci_tipo(annuncio_info['tipo'], 1)
        if not annuncio_info['tipo']:
            app.logger.error('tipo non supportato')
            return redirect(url_for('home'))

        # Prendo gli annunci consigliati in base a quello visualizzato
        consigliati = dbi_annunci.get_consigliati(annuncio_info, PERCORSO_DATABASE)

        # renderizzo il template: i consigliati posso essere da 0 a 4 massimo e solo annunci pubblici
        return render_template('annuncio_singolo.html', utente=utente, annuncio=annuncio_info,
                               prenotazioni=prenotazioni, data_min=data_min, data_max=data_max,
                               consigli=consigliati[0:min(4, len(consigliati)):1])
    else:
        app.logger.error('Non hai i permessi per accedere a questo annuncio')
        return redirect(url_for('home'))


# ---------------------------    MODIFICA DI UN ANNUNCIO PRECEDENTEMENTE INSERITO    ----------------------------------

# Gestisco la pagina di modifica di un annuncio a cui possono accedere solo gli utenti registrati come locatori
# e cui l'id coincide con l'id del creatore dell'annuncio che si vuole modificare
@app.route('/modifica_annuncio/<int:annuncio_id>')
@login_required
def modifica_annuncio(annuncio_id):
    # Prendo i dati dell'annuncio
    annuncio_old = dbi_annunci.get_annuncio_singolo(PERCORSO_DATABASE, annuncio_id)

    # se i permessi sono giusti bene puoi modificare l'annuncio, altrimenti no
    if current_user.is_authenticated and current_user.RUOLO and annuncio_old['locatore'] == current_user.id:
        return render_template('modifica_annuncio.html', annuncio=annuncio_old,
                               utente=current_user, errori=dizionario.crea_errori_corretto_modifica_annuncio())
    else:
        app.logger.error('Non puoi modificare questo annuncio')
        return redirect(url_for('profilo_locatore'))
        # Sarebbe anche plausibile rimandarlo alla pagina: (a seconda delle interpretazioni)
        #         return redirect(url_for('annuncio', annuncio_id=annuncio_id))


# Corretta modifica dell'annuncio
@app.route('/modifica_annuncio_successo/<int:annuncio_id>', methods=['POST'])
@login_required
def modifica_annuncio_successo(annuncio_id):
    # Se tutti i permessi sono okay posso pensare di procedere
    if (request.method == 'POST' and current_user.is_authenticated and current_user.RUOLO == 1
            and current_user.id == dbi_annunci.get_locatore_id_by_annuncio(annuncio_id, PERCORSO_DATABASE)):

        annuncio_mod = request.form.to_dict()

        # Controllo se sono state modificate le foto
        try:
            # Provo a prenderle, se sono state modificate, almeno la prima esisterà, provo ad accedervi
            # se esiste elaboro le modifiche, altrimenti considero come se non fossero state mai toccate
            foto = request.files.getlist('foto')
            if foto[0].filename == "":
                raise ValueError

            # Controllo le foto
            foto = controlli_automatici.foto_nome_uguale(foto)
            # Inizializzo i flag
            errore = 0
            conta = 0
            for picture in foto:
                if not controlli_automatici.controllo_foto_idonea(picture.filename):
                    errore = 1
                    break
                conta = conta + 1

            # Controllo che il numero di foto sia corretto
            if conta < 1 or conta > 5:
                errore = 1
        except ValueError or KeyError:
            # se non ci sono foto uso dei valori fittizi
            errore = 0
            foto = -1

        # inserisco l'id dell'annuncio tra i dati, per avere una scrittura più compatta
        annuncio_mod['annuncio_id'] = annuncio_id
        [annuncio_mod, errori] = controlli_automatici.modifica_annuncio(annuncio_mod)

        error = 0
        for chiave in errori:
            if errori[chiave]:
                error = 1
                break

        # A differenza di form registrazione e form nuovo annuncio, se rilevo un errore NON salvo le modifiche
        if annuncio_mod and not errore and not error:
            if dbi_annunci.inserisci_modifica_annuncio(PERCORSO_DATABASE, PERCORSO_FOTO, foto, annuncio_mod):
                return redirect(url_for('profilo_locatore', username=current_user.NOME, filtro=1))
            else:
                app.logger.error('modifica annuncio non riuscita')
                return render_template('modifica_annuncio.html',  utente=current_user, errori=errori,
                                       annuncio=dbi_annunci.get_annuncio_singolo(PERCORSO_DATABASE, annuncio_id))
        else:
            app.logger.error('modifica annuncio non riuscita')
            return render_template('modifica_annuncio.html',  utente=current_user, errori=errori,
                                       annuncio=dbi_annunci.get_annuncio_singolo(PERCORSO_DATABASE, annuncio_id))
    else:
        app.logger.error('Errore lato server')
        return render_template('modifica_annuncio.html', utente=current_user,
                               errori=dizionario.crea_errori_corretto_modifica_annuncio(),
                               annuncio=dbi_annunci.get_annuncio_singolo(PERCORSO_DATABASE, annuncio_id))


# --------------------------------   PRENOTAZIONE DELLA VISITA AD UN IMMOBILE   -----------------------------------


# Gestisco una nuova prenotazione correttamente inviata
@app.route('/nuova_prenotazione', methods=['POST'])
@login_required
def nuova_prenotazione():
    if request.method == 'POST' and current_user.is_authenticated:
        # Richiedo i dati della prenotazione
        dati = request.form.to_dict()
        try:
            id_annuncio = int(dati['id_annuncio'])
        except ValueError or KeyError:
            app.logger.error('Id annuncio non valido')
            return redirect(url_for('home'))

        # Controllo la correttezza della prenotazione
        dati = controlli_automatici.controllo_nuova_prenotazione(dati, PERCORSO_DATABASE)

        # Se i dati forniti sono corretti, l'annuncio è effettivamente disponibile e il cliente non ha
        # prenotazioni attive (in sospeso o anche confermate [anche per date passate]), e il giorno e l'orario
        # scelti dal locatore sono ancora liberi al momento della prenotazione, allora posso procedere all'inserimento
        if (dati and dbi_annunci.get_annuncio_singolo(PERCORSO_DATABASE, dati['id_annuncio'])['disponibile']
                and not dbi_prenotazioni.check_prenotazioni(PERCORSO_DATABASE, dati['id_annuncio'], current_user.id, 1)
                and dbi_prenotazioni.check_slot_libero(PERCORSO_DATABASE, dati)):

            dati['locatore'] = dbi_annunci.get_locatore_id_by_annuncio(dati['id_annuncio'], PERCORSO_DATABASE)

            # se tutto è corretto sino a ora posso provare a inserire la nuova prenotazione
            if dati['locatore'] and dbi_prenotazioni.aggiungi_nuova_prenotazione(dati, PERCORSO_DATABASE):
                return redirect(url_for('annuncio', annuncio_id=id_annuncio))
            else:
                app.logger.error('Inserimento nuova prenotazione fallito')
                return redirect(url_for('annuncio', annuncio_id=id_annuncio))
        else:
            app.logger.error('prenotazione non riuscita')
            return redirect(url_for('annuncio', annuncio_id=id_annuncio))
    else:
        app.logger.error('Errore lato server')
        return redirect(url_for('home'))


# ------------------------------------   PROFILI ---> PROFILO CLIENTE   ---------------------------------------


# Mi occupo di gestire il profilo cliente
@app.route('/profilo_cliente/<string:username>/<int:filtro>')
@login_required
def profilo_cliente(username, filtro):
    # Controllo che l'utente sia autenticato
    if current_user.is_authenticated:
        # Controllo che l'utente corrente coincida con il possessore del profilo e che il suo ruolo sia adeguato
        if current_user.NOME == username and not current_user.RUOLO:
            # Prendo tutte lre prenotazioni che il cliente ha effettuato
            visite = dbi_prenotazioni.get_prenotazioni_by_cliente(current_user.id, filtro, PERCORSO_DATABASE)

            # Non strettamente necessario, identifico il numero di richieste per tipo
            [attive, accettate, rifiutate] = controlli_automatici.conta_richieste(visite)

            # Aggiungo altri dettagli a quelli già ottenuti dalle prenotazioni per avere un aspetto più gradevole
            visite = dbi_annunci.integrazione_dati_visita(visite, PERCORSO_DATABASE)

            return render_template('profilo_cliente.html', username=username, visite=visite,
                                   pendenti=attive, accettate=accettate, utente=current_user, filtro=filtro,
                                   rifiutate=rifiutate)
        else:
            app.logger.error("Profilo non tuo o Ruolo non adeguato")
            return redirect(url_for('home'))
    else:
        app.logger.error("Devi fare il login per potere entrare nella pagina degli utenti registrati")
        return redirect(url_for('login', errore=False))


# ------------------------------    PROFILI ---> PROFILO LOCATORE   ----------------------------------------


# Ho scelto di fare la pagina cliente e locatore relativamente simili per avere un sito quanto più uniforme
# possibile, inoltre, volevo garantire un interfaccia nota e ben conosciuta a qualsiasi cliente che decidesse
# di diventare locatore e viceversa
@app.route('/profilo_locatore/<string:username>/<int:filtro>')
@login_required
def profilo_locatore(username, filtro):
    # Controllo che l'utente sia correttamente autenticato
    if current_user.is_authenticated:

        # Controllo che il nome corrente dell'utente e il nome del proprietario del profilo coincidano
        # controllo inoltre che il ruolo sia corretto
        if current_user.NOME == username and current_user.RUOLO:
            # Prendo dalla base dati tutte le prenotazioni ricevute dal locatore
            visite = dbi_prenotazioni.get_prenotazioni_by_locatore(current_user.id, PERCORSO_DATABASE)

            # Dò qualche statistica carina sulla natura delle prenotazioni ricevute
            [attive, accettate, rifiutate] = controlli_automatici.conta_richieste(visite)

            # Siccome il locatore si può comportare come cliente, prendo le eventuali prenotazioni effettuate da lui
            visite2 = dbi_prenotazioni.get_prenotazioni_by_cliente(current_user.id, 1, PERCORSO_DATABASE)

            # Dò qualche statistica carina sulla natura delle prenotazioni effettuate
            [attive2, accettate2, rifiutate2] = controlli_automatici.conta_richieste(visite2)

            # Integro i dati delle prenotazioni con i dati dell'annuncio
            visite2 = dbi_annunci.integrazione_dati_visita(visite2, PERCORSO_DATABASE)

            # Integro i dati delle prenotazioni con i dati del locatore verso cui si è fatta la prenotazione
            for i in range(0, len(visite2)):
                visite2[i]['nome_locatore'] = dbi_utenti.get_user_name_by_email(visite2[i]['locatore'],
                                                                                PERCORSO_DATABASE)

            # Prendo tutti gli annunci pubblicati dal locatore
            annunci = dbi_annunci.get_annunci_by_locatore(current_user.id, filtro, PERCORSO_DATABASE)

            # Mostro altre statistiche carine
            [pubblici, privati] = controlli_automatici.conta_annunci(annunci)

            return render_template('profilo_locatore.html', username=username, visite=visite,
                                   filtro=filtro, pubblici=pubblici, privati=privati, rifiutate=rifiutate,
                                   pendenti=attive, accettate=accettate, utente=current_user, annunci=annunci,
                                   visite2=visite2, accettate2=accettate2, rifiutate2=rifiutate2, pendenti2=attive2)
        else:
            app.logger.error("Profilo non tuo o Ruolo non adeguato")
            return redirect(url_for('home'))
    else:
        app.logger.error("Devi fare il login per potere entrare nella pagina degli utenti registrati")
        return redirect(url_for('login', errore=False))


# --------------------    GESTIONE DELLE PRENOTAZIONI: DECISIONE LATO LOCATORE   ------------------------------------

@app.route('/scelta_prenotazioni', methods=['POST'])
@login_required
def scelta_prenotazioni():
    # Controllo che l'utente abbia fatto il login
    if request.method == 'POST' and current_user.is_authenticated:
        try:
            # Controllo che il ruolo sia corretto e che chi ha mandato il form coincida con l'utente corrente
            if current_user.RUOLO and current_user.id == request.form['id_utente']:
                dati2 = request.form.to_dict()

                dati = dict()
                for dato in dati2:
                    if dato != 'id_utente':
                        dati[dato] = dati2[dato]

                # Se il locatore ha premuto conferma a form vuoto lo gestisco
                if not len(dati):
                    return redirect(url_for('profilo_locatore', filtro=1,
                                username=dbi_utenti.get_user_name_by_email(dati2['id_utente'], PERCORSO_DATABASE)))

                # Elaboro le prenotazioni ricevute
                dati = controlli_automatici.elabora_prenotazioni(dati)

                # Controllo che la gestione delle prenotazioni fatta dal locatore sia sensata
                dati = controlli_automatici.valida_scelte_locatore_prenotazioni(dati, PERCORSO_DATABASE)

                # se tutto è corretto posso pensare di aggiornare la prenotazione della base dati
                if dati:
                    if dbi_prenotazioni.aggiorna_prenotazioni(dati, current_user.id, PERCORSO_DATABASE):
                        return redirect(url_for('profilo_locatore', username=current_user.NOME, filtro=1))
                    else:
                        app.logger.error('scelta prenotazioni non riuscita')
                        return redirect(url_for('profilo_locatore', username=current_user.NOME, filtro=1))
                else:
                    app.logger.error('scelta prenotazioni non riuscita')
                    return redirect(url_for('profilo_locatore', username=current_user.NOME, filtro=1))
            else:
                app.logger.error('scelta prenotazioni non riuscita')
                return redirect(url_for('profilo_locatore', username=current_user.NOME, filtro=1))
        except KeyError or ValueError:
            app.logger.error('scelta prenotazioni non riuscita')
            return redirect(url_for('profilo_locatore', username=current_user.NOME, filtro=1))
    else:
        app.logger.error('scelta prenotazioni non riuscita')
        return redirect(url_for('profilo_locatore', username=current_user.NOME, filtro=1))
