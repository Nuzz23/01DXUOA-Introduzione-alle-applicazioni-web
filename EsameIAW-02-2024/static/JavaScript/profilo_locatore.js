// Scatta al completo caricamento dell'intera pagina
window.onload = function() {
    const bottone = document.getElementById('visualizza_pendenti')

    // Se il numero di richieste pendenti è maggiore di 0, allora per attirare l'attenzione del locatore verso lo stesso
    // anziché usare pop-up invasivi, ho preferito fare alternare il colore del bottone delle richieste pendenti
    if(pendenti>0)
        setInterval(function() {
            // ogni dato intervallo cambio tra la grafica mia del bottone e quella di btn-danger di bootstrap
            if(bottone.classList.contains('btn-mio')) {
                bottone.classList.remove('btn-mio');
                bottone.classList.add('btn-danger');
            } else {
                bottone.classList.remove('btn-danger');
                bottone.classList.add('btn-mio');
            }
        }, 1000); // Esegui la funzione ogni 1000 millisecondi (1 secondo)


    // Funzione per gestire il cambiamento di stato dei radio button
    function cambio_rifiuto(event) {
        // definisco i vari elementi del dom con cui mi interessa interagire
        // PS non bello farlo con i target a nome variabile...
        const i = event.target.name.replace('scelta-', '');
        const motivazione = document.getElementById(`motivazione-${i}`);
        const motivo = document.getElementById(`motivo-${i}`);
        let positivo = document.getElementById(`scelta-positiva-label-${i}`)
        let negativo = document.getElementById(`scelta-negativa-label-${i}`)
        let posponi = document.getElementById(`posponi-label-${i}`)

        // Verifica che gli elementi esistano prima di accedere alle loro proprietà
        if(motivazione && motivo)
            if (event.target.id !== `scelta-negativa-${i}`)
                motivazione.classList.remove('presente-rifiuto');
            else
                motivazione.classList.add('presente-rifiuto');

        // se si sceglie di rifiutare la visita, evidenzio la scelta e faccio comparire il campo motivazione
        // rendendolo obbligatorio e gestendone i parametri di lunghezza
        if (event.target.id === `scelta-negativa-${i}`) {
            negativo.classList.add('bold');
            positivo.classList.remove('bold');
            posponi.classList.remove('bold');
            motivo.required=true;
            motivo.minLength=6;
            motivo.maxLength=100;
        }
        // altrimenti potrei avere scelto di accettare, allora evidenzio la scelta e faccio scomparire, se presente,
            // la casella di input dove inserire la motivazione (entrambe accetta e posponi)
        else{
            if (event.target.id === `scelta-positiva-${i}`) {
                positivo.classList.add('bold');
                posponi.classList.remove('bold');
            }
            // se la scelta è quella di posporre evidenzio invece quel campo
            else {
                posponi.classList.add('bold');
                positivo.classList.remove('bold');
            }
            negativo.classList.remove('bold');
            motivo.required=false;
            motivo.minLength=0;
        }
    }

    // Aggiungo gli event listener ai radio button per vedere quando l'utente cambia la sua scelta
    document.querySelectorAll('input[type=radio]').forEach((radio) => {
        radio.addEventListener('change', cambio_rifiuto);
    });
};
