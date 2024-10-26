def check_validity(password):
    maiuscole = False
    minuscole = False
    numeri = False
    speciali = False
    strange = False
    for lettera in password:
        if 'a' <= lettera <= 'z':
            minuscole = True
        elif 'A' <= lettera <= 'Z':
            maiuscole = True
        elif lettera in '#@$£%&€':
            speciali = True
        elif '0' <= lettera <= '9':
            numeri = True
        else:
            strange = True

    if maiuscole and speciali and numeri and minuscole and not strange:
        return True
    return False
