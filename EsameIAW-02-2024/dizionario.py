from datetime import datetime


# Creo la struttura dati per gestire gli errori sulla registrazione inizialmente vuota
def crea_dizionario_registrazione_vuoto():
    campi = {
        'email': '',
        'nome': '',
        'telefono': '',
        'ruolo': 2
    }

    return campi


# Traduco i locali nel caso siano 5+
def traduci_locali(locali, metodo):
    if metodo:
        try:
            if int(locali) == 6:
                return ('5+')
            else:
                return str(locali)
        except ValueError:
            return 1
    else:
        try:
            if locali == '5+':
                return 6
            else:
                return int(locali)
        except ValueError:
            return 1


# Funzione che controlla la correttezza di una data
def controlla_data_valida(giorno, mese, anno):
    # Verifica se l'anno è bisestile
    try:
        anno = int(anno)
        mese = int(mese)
        giorno = int(giorno)
        if (anno % 4 == 0 and anno % 100 != 0) or (anno % 400 == 0):
            giorni_in_mese = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:
            giorni_in_mese = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        # Verifica se il mese e il giorno sono validi
        if 1 <= mese <= 12 and 1 <= giorno <= giorni_in_mese[mese - 1] and anno >= 2024:
            return 1  # Data valida
        raise ValueError
    except ValueError or KeyError or TypeError:
        return 0  # Data non valida


# Creo la struttura dati per gestire gli errori sulla creazione del nuovo post, caso nessun errore o errori non
# verificabili
def crea_errori_corretto():
    campi = {
        'disponibile': 2,
        'arredata': 2,
        'descrizione': 2,
        'locali': 2,
        'indirizzo': 2,
        'tipo_strada': 2,
        'civico': 2,
        'titolo': 2,
        'tipo': 2
    }

    return campi


# Creo la struttura dati per gestire gli errori sulla creazione del nuovo post, caso nessun errore o errori non
# verificabili
def crea_errori_corretto_modifica_annuncio():
    campi = {
        'disponibile': 0,
        'arredata': 0,
        'descrizione': 0,
        'locali': 0,
        'titolo': 0,
        'tipo': 0
    }

    return campi


# Traduco l'errore da stringa a numero e viceversa
def traduci_errore(errore, metodo):
    if metodo:
        errori_tradotto = dict()

        errori_tradotto['email'] = int(errore[0])
        errori_tradotto['password'] = int(errore[1])
        errori_tradotto['nome'] = int(errore[2])
        errori_tradotto['telefono'] = int(errore[3])
        errori_tradotto['ruolo'] = int(errore[4])
    else:
        errori_tradotto = (str(errore['email']) + str(errore['password']) + str(errore['nome']) +
                           str(errore['telefono']) + str(errore['ruolo']))

    return errori_tradotto


# traduco i turni da numero a valore e viceversa
def traduci_turni(valore, metodo):
    # Traduco il turno da valore numerico a valore in ore
    if metodo == 1:
        if valore == 0:
            return '9-12'
        elif valore == 1:
            return '12-14'
        elif valore == 2:
            return '14-17'
        elif valore == 3:
            return '17-20'
        else:
            return False
    # Traduco il turno da orario a valore numerico
    elif not metodo:
        if valore == '9-12':
            return 0
        elif valore == '12-14':
            return 1
        elif valore == '14-17':
            return 2
        elif valore == '17-20':
            return 3
        else:
            return False

    return False


# Creo una matrice di prenotazioni inizialmente libera
def crea_prenotazioni():
    giorni = 7
    num_turni = ['9-12', '12-14', '14-17', '17-20']
    turni = list()
    for i in range(0, giorni, 1):        # Sette giorni della settimana
        turni.append(list(num_turni))

    return turni


# traduco il tipo di immobile da numero a valore e viceversa
def traduci_tipo(valore, metodo):
    # Traduco il tipo da valore numerico a nome
    if metodo == 1:
        try:
            valore = int(valore)
        except ValueError:
            return False

    if metodo == 1:
        if valore == 0:
            return 'Casa indipendente'
        elif valore == 1:
            return 'Appartamento'
        elif valore == 2:
            return 'Loft'
        elif valore == 3:
            return 'Villa'
        else:
            return False
    # Traduco il tipo da nome a valore numerico
    elif not metodo:
        if valore == 'Casa indipendente':
            return 0
        elif valore == 'Appartamento':
            return 1
        elif valore == 'Loft':
            return 2
        elif valore == 'Villa':
            return 3
        else:
            return False

    return False


# ordinamento delle prenotazioni in base alla data/turno/progressivo
# Fatto rigorosamente con un sorting linearitmico in loco
def quick_sort(dati):

    lista_ordinata = sorted(dati,
                            key=lambda d: (datetime.strptime(d['data'], '%d-%m-%Y'),
                                           traduci_turni(d['orario'], 0), d['progressivo']), reverse=True)

    return lista_ordinata
