
// controllo e aggiorno le disponibilità
function aggiorna() {
    // Prendo la data scelta dall'utente
    let data_scelta = new Date(document.getElementById("data").value);

    // Prendo i valori option della select il campo select
    let elenco_orari = document.getElementById("orario");

    // prendo la data di oggi
    let oggi = new Date();         //soluzione alternativa, set date all'una di notte GMT+1
    let i = 0                   // inizializzo il contatore
    oggi.setDate(oggi.getDate()+1);    //  Iniziamo con la prima data possibile, ovvero domani

    for(; i<7; i++)
        if ((oggi.getDate()) === (data_scelta.getDate()))
            break
        else
            oggi.setDate(oggi.getDate() +1);

    // Tolgo le opzioni già create per l'elenco degli orari (select)
    while (elenco_orari.firstChild) {
        elenco_orari.removeChild(elenco_orari.firstChild);
    }

    let failed = 0    // Inizializzo il contatore del fallimento

    // Aggiungo le "nuove" opzioni al campo select
    for (let j = 0; j < opzioni[i].length; j++) {
        // controllo che non sia già stato preso l'orario
        if (opzioni[i][j] !== 0) {       // li converto con il !== in interi
            // se si creo l'opzione
            let option = document.createElement("option");
            option.value = j.toString();    // gli assegno il valore della costante del ciclo, purtroppo come stringa, la converto in python
            option.text = opzioni[i][j]; // mosto all'utente il valore dell'orario
            elenco_orari.appendChild(option);    // aggiungo l'opzione
        }
        else
            failed = failed + 1   // Per ogni fallimento incremento il contatore

        // Se un giorno è completamente riempito!
        if (failed === 4){
            let option = document.createElement("option");
            option.value = (-1).toString()
            option.text = 'prenotazioni riempite per questo giorno'
            elenco_orari.appendChild(option);
        }
    }
}

// mi assicuro di runnare i comandi a pagina creata (ho scoperto dopo qualche rogna il perché si faccia ;) )
window.onload = function() {
    // Gestisci il modale (apertura e chiusura)
    const myModal = document.getElementById('myModal');
    const myInput = document.getElementById('myInput');

    // se trova il modale, va gestito
    if(myModal) {
        myModal.addEventListener('shown.bs.modal', () => {
            myInput.focus();
        });
    }

    // Aggiungo un event listener alla data per chiamare aggiorna ogni volta che la data viene cambiata
    document.getElementById("data").addEventListener("change", aggiorna);

}
