from flask_login import UserMixin


# Gestione dell'utente come una classe a oggetti
class User(UserMixin):
    # Creazione del costruttore (inizializzatore) della classe User
    def __init__(self, email, nome, password, ruolo, cognome):
        # Campi del costruttore
        self.id = email
        self.NOME = nome
        self.PASSWORD = password
        self.RUOLO = int(ruolo)
        self.COGNOME = cognome
