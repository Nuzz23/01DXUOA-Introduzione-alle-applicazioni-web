from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, email, nome, password, ruolo, telefono):
        self.id = email
        self.NOME = nome
        self.PASSWORD = password
        self.RUOLO = int(ruolo)
        self.TELEFONO = telefono
