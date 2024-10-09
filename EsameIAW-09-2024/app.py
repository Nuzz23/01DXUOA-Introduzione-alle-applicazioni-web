# Librerie usate
# Permette di definire l'oggetto utente
from models import User
# Libreria principale di flask
from flask import Flask, render_template, redirect, url_for, request, flash
# Libreria di flask usata per la gestione del login/registrazione/logout dell'utente
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
# Libreria legata alla sicurezza delle password
from werkzeug.security import generate_password_hash, check_password_hash
# Libreria per la gestione della data e dell'ora
from datetime import datetime
# File contenente tutte le interazioni con la base dai
import interazioniBD

app = Flask(__name__)

# Inizializzo il login manager e la chiave segreta
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'segreto'

BASEDATI = "BaseDati/BaseDati.db"  # Percorso per raggiungere la base dati


# Gestisco la home page del sito (route standard)
@app.route('/')
def home():
    # Placeholder per esercizio
    esercizi = ''

    # Controllo se l'utente ha fatto o meno il login (per definire cosa sarà utente)
    if current_user.is_authenticated:
        utente = current_user
        # Se l'utente è un allenatore (RUOLO = 1) potrà visionare nella home page
        # Tutti gli allenamenti creati da lui (sia pubblici che privati) e tutti quelli pubblici creati da altri
        # ordinati in maniera decrescente per data di creazione
        if utente.RUOLO:
            # Trovo tutti gli esercizi (specifico chi è l'allenatore per sapere quali prendere come privati)
            esercizi = interazioniBD.trova_tutti_esercizi(utente.id, BASEDATI)
    else:
        utente = ''

    # Renderizzo il template della home passando come parametri utente ed esercizi
    return render_template('home.html', utente=utente, esercizi=esercizi)


# Riporto alla pagina di login (con errori come discriminante)
@app.route('/login/<int:errore>')
def login(errore):
    return render_template('login.html', errore=errore)


# Faccio il login utente
@app.route('/login_success', methods=['POST'])
def login_success():
    # Prendo i dati del login dal form come dizionario
    dati = request.form.to_dict()

    # separo i campi di login contenenti email e password pulendoli da spazi
    try:
        username = dati['EMAIL'].strip()
        password = dati['PASSWORD'].strip()
    except KeyError or ValueError:
        return redirect(url_for('login', errore=True))

    # Controllo la presenza dell'utente nella base dati
    if not interazioniBD.controllo_presenza_utente(username, BASEDATI):
        app.logger.error('Mail e/o password non valida')
        return redirect(url_for('login', errore=True))

    # controllo la correttezza della password
    if not check_password_hash(interazioniBD.password_corretta(username, BASEDATI), password):
        app.logger.error('Mail e/o password non valida')
        return redirect(url_for('login', errore=True))

    # Prendo i dati utente presenti nella mia base dati
    dati = interazioniBD.get_dati_utente(username, BASEDATI)

    # controllo che non ci sia stato qualche errore nel trovare l'utente
    if not dati:
        app.logger.error('Mail o/e password non valide')
        return redirect(url_for('login', errore=True))

    # eseguo il login dell'utente
    dati = User(email=dati['EMAIL'], password=dati['PASSWORD'], cognome=dati['COGNOME'],
                ruolo=dati['RUOLO'], nome=dati['NOME'])
    login_user(dati, True)

    # porto alla schermata home dopo un login corretto
    return redirect(url_for('home'))


# Definisco lo userLoader e i vari campi
@login_manager.user_loader
def load_user(user_id):
    # carico i dati utente data l'email (user_id)
    db_user = interazioniBD.get_dati_utente(user_id, BASEDATI)

    # Creo l'oggetto utente passando questi parametri
    user = User(email=db_user['EMAIL'], nome=db_user['NOME'], password=db_user['PASSWORD'], ruolo=db_user['RUOLO'],
                cognome=db_user['COGNOME'])

    return user


# logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# Prima parte della registrazione
@app.route('/register/<int:errore>')
def register(errore):
    return render_template('register.html', errore=errore)


# Mi occupo della registrazione di un utente validando i dati
@app.route('/register_success', methods=['POST'])
def register_success():
    # Controllo la correttezza dei dati
    dati = request.form.to_dict()

    # Controllo la correttezza dei dati ottenuti
    risposta = interazioniBD.controlla_nuovo_utente(dati, BASEDATI)

    # se tutti i controlli sono passati posso provare a inserire l'utente nella base dati
    if not risposta:
        # Creo l'hash della password
        dati['PASSWORD'] = generate_password_hash(dati['PASSWORD'])
        # Inserisco l'utente nella base dati
        if interazioniBD.inserisci_nuovo_utente(dati, BASEDATI):
            # Creo l'oggetto user
            dati = User(email=dati['EMAIL'], password=dati['PASSWORD'], cognome=dati['COGNOME'], ruolo=dati['RUOLO'],
                        nome=dati['NOME'])
            # faccio il login utente
            login_user(dati, True)
            return redirect(url_for('home'))
        else:
            return render_template('register.html', errore=2)
    else:
        return render_template('register.html', errore=risposta)


# Pagina per la visita del profilo privato allenatore
@app.route("/Allenatore<string:errore>")
@login_required
def profilo_allenatore(errore):
    # Controllo che l'utente abbia il ruolo corretto
    if current_user.is_authenticated and current_user.RUOLO:
        # Trovo tutti gli esercizi sia privati che pubblici del singolo personal
        esercizi = interazioniBD.trova_esercizi_personal(current_user.id, BASEDATI)
        # Converto gli id in str da int per problemi di concatenazione int-str
        for i in range(0, len(esercizi), 1):
            esercizi[i]['ID'] = str(esercizi[i]['ID'])
        # Creo il template, invocando, nell'ordine la funzione che calcola il ranking dell'allenatore
        # Quella che trova tutti i clienti associato a un dato allenatore (se presenti), gli esercizi trovati prima
        # le schede create dall'allenatore (se presenti)
        # Mi assicuro che ci siano almeno 2 esercizi per creare una nuova scheda, altrimenti disattivo l'opzione
        return render_template("ProfiloAllenatore.html", utente=current_user, errore=errore,
                               ranking=interazioniBD.ranking_allenatore(current_user.id, BASEDATI),
                               clienti=interazioniBD.trova_clienti_personal(current_user.id, BASEDATI),
                               esercizi=esercizi,
                               scheda=interazioniBD.trova_schede_allenatore(current_user.id, BASEDATI),
                               abbastanza_esercizi=(len(interazioniBD.trova_tutti_esercizi(current_user.id, BASEDATI)) > 1))
    else:
        return redirect(url_for('home'))


# Pagina del profilo utente
@app.route("/Cliente")
@login_required
def profilo_cliente():
    # Controllo che il ruolo dell'utente sia quello corretto
    if current_user.is_authenticated and not current_user.RUOLO:
        # Controllo se il cliente non ha assegnato un personal trainer
        if interazioniBD.cliente_cerca_personal(current_user.id, BASEDATI):
            # Se si trovo tutti i personal trainer presenti
            cerca = True
            personal = interazioniBD.trova_tutti_personal_trainer(BASEDATI)
            scheda = False
        else:
            # Se no trovo i dettagli del singolo personal trainer a cui è assegnato
            cerca = False
            personal = interazioniBD.trova_personal_dato_cliente(current_user.id, BASEDATI)
            # Trovo le eventuali schede fatte al cliente
            scheda = interazioniBD.trova_schede_cliente(current_user.id, BASEDATI)

        return render_template("ProfiloCliente.html", utente=current_user,
                               cerca=cerca, personal=personal, scheda=scheda)
    else:
        return redirect(url_for('home'))


# Permetto la assunzione immediata di un personal trainer
@app.route("/assumi_personal", methods=['POST'])
@login_required
def assumi_personal():
    # Controllo che l'utente che ha fatto richiesta sia un cliente e che cerchi effettivamente un personal trainer
    # se si provo ad assegnarlo
    if (current_user.is_authenticated and not current_user.RUOLO
            and interazioniBD.cliente_cerca_personal(current_user.id, BASEDATI) and
            not interazioniBD.assegna_personal(current_user.id, (request.form.to_dict())["PERSONA"], BASEDATI)):
        app.logger.error("Personal trainer NON assegnato")
        flash("personal trainer non assegnato", category="error")

    return redirect(url_for('profilo_cliente'))


# Tramite questa route permetto la creazione del nuovo esercizio
@app.route("/nuovo_esercizio", methods=['POST'])
@login_required
def nuovo_esercizio():
    # Controllo che il ruolo sia corretto
    if current_user.is_authenticated and current_user.RUOLO:
        # Prendo i dati dal form e li valido
        dati = request.form.to_dict()
        errore = interazioniBD.valida_nuovo_esercizio(dati)
        # Controllo l'assenza di errori
        if '1' not in errore and errore != '':
            # Se tutto okay, provo a inserire l'esercizio nella base dati, indicando anche da chi è stato
            # creato e data + ora della creazione (per ordinarli quando mostrati)
            if interazioniBD.inserisci_nuovo_esercizio(dati, current_user.id, datetime.now(), BASEDATI):
                flash("Esercizio valido", category="success")
                return redirect(url_for('profilo_allenatore', errore='00'))
            else:
                flash("Esercizio non inserito", category="error")
                app.logger.error("Esercizio non inserito")
                return redirect(url_for('profilo_allenatore', errore='11'))
        else:
            app.logger.error("Esercizio non inserito")
            flash("Esercizio non inserito", category="error")
            return redirect(url_for('profilo_allenatore', errore=errore[0:2:1] if errore != '' else '11'))
    return redirect(url_for('profilo_allenatore', errore='00'))


# Modifica un esercizio già creato
@app.route("/modifica_esercizio<string:data>")
@login_required
def modifica_esercizio(data):
    # prendo il singolo esercizio tramite l'id nel link
    # nota, viene "splittato" per separarlo dai flag di errore
    try:
        dati = interazioniBD.get_singolo_esercizio(int(data.split('-')[0].strip()), BASEDATI)
        errore = data.split('-')[1].strip()
    except Exception:
        return redirect(url_for('profilo_allenatore', errore='00'))
    # Mi accerto che il ruolo sia corretto e che chi faccia richiesta sia chi ha creato l'esercizio
    if dati and current_user.is_authenticated and current_user.RUOLO and current_user.id == dati['EMAIL']:
        return render_template('modifica_esercizio.html', utente=current_user,
                           esercizio=dati, errore=errore)
    else:
        return redirect(url_for('profilo_allenatore', errore='00'))


# Controlla la correttezza dopo l'invio del form di modifica di un esercizio
@app.route("/modifica_esercizio_success<int:val>", methods=['POST'])
@login_required
def modifica_esercizio_success(val):
    # prendo i dati dell'esercizio come da base dati (no modifiche)
    dati = interazioniBD.get_singolo_esercizio(val, BASEDATI)
    # Controllo che l'utente sia chi ha creato l'esercizio e con il ruolo giusto
    if dati and current_user.is_authenticated and current_user.RUOLO and current_user.id == dati['EMAIL']:
        # Prendo i dati dell'esercizio e li valido con la stessa funzione della creazione
        dati2 = request.form.to_dict()
        errore = interazioniBD.valida_nuovo_esercizio(dati2)
        # Controllo l'assenza di errori
        if '1' not in errore and errore != '':
            # se non ci sono errori procedo a inserirlo
            if interazioniBD.modifica_esercizio(dati, dati2, BASEDATI):
                return redirect(url_for('profilo_allenatore', errore='00'))
            else:
                flash("Esercizio non inserito", category="error")
                app.logger.error("Esercizio non inserito")
                return redirect(url_for('modifica_esercizio', data=str(val)+'-11'))
        else:
            if errore == '':
                errore = '11'
            return redirect(url_for('modifica_esercizio', data=str(val)+'-'+errore))
    else:
        return redirect(url_for('profilo_allenatore', errore='00'))


# Elimina un esercizio già creato
@app.route("/elimina_esercizio<int:val>")
@login_required
def elimina_esercizio(val):
    # Prendo i dati dell'esercizio da eliminare
    es = interazioniBD.get_singolo_esercizio(val, BASEDATI)
    # Controllo che l'utente un allenatore e che abbia creato lui l'esercizio
    if current_user.is_authenticated and current_user.RUOLO and es and es['EMAIL'] == current_user.id:
        # provo a eliminarlo dalla base dati
        if interazioniBD.elimina_esercizio(val, BASEDATI):
            flash("Esercizio eliminato", category="success")
            return redirect(url_for('profilo_allenatore', errore='00'))
        else:
            flash("Esercizio non eliminato", category="error")
            app.logger.error("Esercizio non eliminato")
            return redirect(url_for('profilo_allenatore', errore='00'))
    else:
        app.logger.error("Esercizio non eliminato")
        return redirect(url_for('profilo_allenatore', errore='00'))


# Permetto all'allenatore di creare una nuova scheda
@app.route("/nuova_scheda")
@login_required
def nuova_scheda():
    # Controllo che l'utente abbia il ruolo corretto
    if current_user.is_authenticated and current_user.RUOLO:
        # controllo i clienti che l'allenatore ha (ne serve almeno 1 a cui associare la scheda)
        clienti = interazioniBD.trova_clienti_personal(current_user.id, BASEDATI)
        if len(clienti) > 0:
            # Permetto la creazione della nuova scheda, inoltre carico tutti gli esercizi creati dal dato allenatore
            # e tutti gli altri di pubblico dominio
            return render_template('nuova_scheda.html', utente=current_user, allenatore=current_user.id,
                               clienti=clienti,
                               esercizi=interazioniBD.trova_tutti_esercizi(current_user.id, BASEDATI))
        else:
            app.logger.error("Nessun cliente")
            flash("Nessun cliente", category="error")
            return redirect(url_for('profilo_allenatore', errore='00'))
    else:
        app.logger.error("Permessi sbagliati")
        flash("Permessi sbagliati", category="error")
        return redirect(url_for('profilo_allenatore', errore='00'))


# Controllo la corretta creazione di una nuova scheda
@app.route("/nuova_scheda_success", methods=['POST'])
@login_required
def nuova_scheda_success():
    # Controllo i permessi dell'utente
    if current_user.is_authenticated and current_user.RUOLO:
        # richiedo i dati del form
        dati = request.form.to_dict()
        # Controllo che il cliente per cui è fatta la scheda sia assegnato all'allenatore che la fa e che l'allenatore
        # sia l'utente corrente
        if ((dati['CLIENTE'] in [cliente['EMAIL'] for cliente in interazioniBD.trova_clienti_personal(current_user.id, BASEDATI)])
                and (dati['ALLENATORE'] == current_user.id)):

            esercizi = set()
            # Prendo tutti gli id degli allenamenti inseriti nella scheda (controllo che esista nella base dati)
            for chiave in dati:
                try:
                    if not interazioniBD.controllo_presenza_esercizio(int(chiave), BASEDATI):
                        raise ValueError
                    esercizi.add(int(chiave))
                    esercizi.add(int(dati[chiave]))
                except ValueError:
                    continue

            # Prendo tutti i possibili allenamenti tra cui scegliere
            presenti = set()
            for elemento in interazioniBD.trova_tutti_esercizi(current_user.id, BASEDATI):
                presenti.add(int(elemento['ID']))

            # Controllo che ogni esercizio scelto sia presente tra quelli disponibili
            for esercizio in esercizi:
                if esercizio not in esercizi:
                    flash("Scheda non inserita", category="error")
                    app.logger.error("Scheda non inserita")
                    return redirect(url_for('nuova_scheda'))

            # Controllo che vi siano almeno due esercizi, se si provo a inserire la scheda
            if (len(esercizi) > 1
                    and interazioniBD.inserisci_nuova_scheda(current_user.id, dati['CLIENTE'], esercizi, BASEDATI)):
                return redirect(url_for('profilo_allenatore', errore='00'))
            else:
                flash("Scheda non inserita", category="error")
                app.logger.error("Scheda non inserita")
                return redirect(url_for('nuova_scheda'))
        else:
            flash("Scheda non inserita", category="error")
            app.logger.error("Scheda non inserita")
            return redirect(url_for('nuova_scheda'))
    else:
        flash("Scheda non inserita", category="error")
        app.logger.error("Scheda non inserita")
        return redirect(url_for('profilo_allenatore', errore='00'))


# Permetto di visualizzare una scheda già creata
@app.route("/visualizza_scheda<int:val>")
@login_required
def visualizza_scheda(val):
    # Controllo che l'utente sia identificato
    if current_user.is_authenticated:
        # Prendo la scheda richiesta
        scheda = interazioniBD.get_scheda(val, BASEDATI)
        # Controllo che l'utente sia o l'allenatore o il cliente per cui è fatta la scheda
        if ((current_user.RUOLO and scheda and scheda['ALLENATORE'] == current_user.id)
                or (not current_user.RUOLO and scheda['CLIENTE'] == current_user.id)) and scheda:
            return render_template('visualizza_scheda.html', utente=current_user,
                                scheda=scheda)
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))


# Permetto di valutare una scheda
@app.route("/valuta_scheda<int:val>", methods=['POST'])
@login_required
def valuta_scheda(val):
    # Controllo il ruolo corretto
    if current_user.is_authenticated and not current_user.RUOLO:
        # Prelevo il rating
        dati = request.form.to_dict()

        # Controllo la correttezza del rating
        try:
            rating = float(dati['RATE'])
            if rating < 1 or rating > 5:
                raise ValueError
        except ValueError:
            flash("Rating invalido", category="error")
            app.logger.error("Rating invalido")
            return redirect(url_for('visualizza_scheda', val=val))

        # Inserisco la valutazione all'interno della scheda
        if interazioniBD.valuta_scheda(val, rating, BASEDATI):
            return redirect(url_for('visualizza_scheda', val=val))
        else:
            flash("Rating invalido", category="error")
            app.logger.error("Rating invalido")
            return redirect(url_for('visualizza_scheda', val=val))
    else:
        app.logger.error("Utente non valido")
        return redirect(url_for('home'))


# Elimina una scheda di allenamento
@app.route("/elimina_scheda<int:val>")
@login_required
def elimina_scheda(val):
    # Trovo la scheda da eliminare
    scheda = interazioniBD.get_scheda(val, BASEDATI)
    # Controllo che la scheda sia stata creata dall'utente che la vuole eliminare
    if current_user.is_authenticated and current_user.RUOLO and scheda and current_user.id == scheda['ALLENATORE']:
        # Provo ad eliminar
        if interazioniBD.elimina_scheda(val, scheda['RATING'], scheda['ALLENATORE'], BASEDATI):
            return redirect(url_for('profilo_allenatore', errore='00'))
        else:
            flash("Scheda non eliminata", category="error")
            app.logger.error("Scheda non eliminata")
            return redirect(url_for('visualizza_scheda', val=val))
    else:
        flash("Scheda non eliminata", category="error")
        app.logger.error("Scheda non eliminata")
        return redirect(url_for('visualizza_scheda', val=val))


# Permette di modificare una scheda già esistente
@app.route("/modifica_scheda<int:val>")
@login_required
def modifica_scheda(val):
    # Trovo la scheda
    scheda = interazioniBD.get_scheda(val, BASEDATI)
    # Controllo che l'allenatore che vuole modificare la scheda sia lo stesso che l'ha fatta
    if current_user.is_authenticated and current_user.RUOLO and scheda and current_user.id == scheda['ALLENATORE']:
        # Trovo tutti gli esercizi possibili da aggiungere alla scheda
        esercizi = interazioniBD.trova_tutti_esercizi(current_user.id, BASEDATI)
        presenti = set()

        for esercizio in scheda['ESERCIZI']:
            presenti.add(esercizio['ID'])

        # Trovo i duplicati (ovvero gli esercizi già presenti nella scheda)
        duplicati = set()
        for i in range(0, len(esercizi), 1):
            if esercizi[i]['ID'] in presenti:
                duplicati.add(i)

        # Rimuovo i duplicati dagli esercizi trovati prima (per non vederli due volte)
        for item in sorted(duplicati, reverse=True):
            esercizi.pop(item)

        return render_template('modifica_scheda.html', scheda=scheda, utente=current_user,
                               esercizi=esercizi)
    else:
        app.logger.error("Utente non valido")
        return redirect(url_for('profilo_allenatore', errore='00'))


# Modifica con successo di una scheda (e controllo dei valori)
@app.route("/modifica_scheda_success<int:val>", methods=['POST'])
@login_required
def modifica_scheda_success(val):
    # Prendo la scheda da modificare
    scheda = interazioniBD.get_scheda(val, BASEDATI)
    # Controllo che l'utente che vuole modificare la scheda sia la stessa che l'ha creata
    if current_user.is_authenticated and current_user.RUOLO and scheda and scheda['ALLENATORE'] == current_user.id:
        # Prelevo i dati dal form
        dati = request.form.to_dict()
        # Controllo che cliente e allenatore siano rimasti invariati
        if scheda['CLIENTE'] == dati['CLIENTE'] and scheda['ALLENATORE'] == dati['ALLENATORE']:
            id_es_scelti = set()
            # Prendo tutti gli esercizi scelti e ne controllo la presenza nella base dati
            for chiave in dati:
                try:
                    if not interazioniBD.controllo_presenza_esercizio(int(chiave), BASEDATI):
                        raise ValueError
                    id_es_scelti.add(int(chiave))
                    id_es_scelti.add(int(dati[chiave]))
                except ValueError:
                    continue

            # Creo la stringa con tutti gli esercizi scelti (da inserire)
            esercizi = ""
            for esercizio in id_es_scelti:
                esercizi = esercizi + str(esercizio) + ", "

            # Mi assicuro che siano stati scelti almeno due esercizi e inserisco la nuova scheda nella base dati
            if len(id_es_scelti) > 1 and interazioniBD.modifica_scheda(val, esercizi[0:len(esercizi)-2:1], BASEDATI):
                return redirect(url_for('visualizza_scheda', val=val))
            else:
                flash("Scheda non modificata", category="error")
                app.logger.error("Scheda non modificata")
                return redirect(url_for('visualizza_scheda', val=val))
        else:
            app.logger.error("Cliente o allenatore invalido")
            flash("Cliente o allenatore non valido", category="error")
            return redirect(url_for('visualizza_scheda', val=val))
    else:
        app.logger.error("Utente non valido")
        flash("Utente non valido", category="error")
        return redirect(url_for('visualizza_scheda', val=val))
