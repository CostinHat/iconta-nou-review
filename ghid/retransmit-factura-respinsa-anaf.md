---
title: "Cum retransmit o factură respinsă de ANAF"
description: O factură respinsă nu se retrimite singură — nici la eroare de structură, nici la eroare de încărcare. Corectezi cauza și apeși din nou manual, factură cu factură; nu există reîncercare automată.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum retransmit o factură respinsă de ANAF

O factură respinsă rămâne respinsă până o retrimiți manual — sistemul nu reîncearcă singur, indiferent de motivul respingerii. Contează însă să identifici exact la ce pas a picat, pentru că pașii de corectare diferă.

## Temeiul legal

::: ghid-temei
**Legea nr. 227/2015 — Codul fiscal**, art. 330 — corectarea documentelor: factura netransmisă beneficiarului se anulează și se emite alta; factura deja transmisă (acceptată în sistem) nu se mai anulează, ci se corectează printr-o factură de stornare sau printr-o factură doar pentru diferență.
:::

## Respinsă la validarea de structură (înainte de a ajunge la ANAF)

Trimiterea trece întâi prin validatorul public ANAF. Dacă structura nu e conformă — un câmp lipsă, un cod greșit, un format nerespectat — **nu se face niciun upload**: „nu trimitem gunoi" e regula explicită a mecanismului de trimitere. Factura rămâne netrimisă oficial, iar mesajele exacte de eroare ale validatorului sunt afișate.

Retransmiterea aici e directă: corectezi datele facturii pe baza mesajului de eroare și apeși din nou „Trimite în SPV". Nu a existat niciun document oficial la ANAF până acum, deci nu e nevoie de stornare — doar de corectare și reîncărcare.

## Respinsă la încărcare (după ce a trecut de validare)

Dacă structura a trecut de validator, dar upload-ul propriu-zis la ANAF eșuează — de exemplu la o problemă de comunicare — factura rămâne marcată cu eroare de încărcare, vizibilă prin semaforul roșu din ecranul de facturi. **Sistemul nu reîncearcă singur.** Retransmiterea cere din nou un click manual pe „Trimite în SPV" — factura reintră prin aceleași verificări (token activ, validare, verificare de trimitere deja activă) înainte de un nou upload.

## Când NU poți retransmite din ecranul obișnuit

Dacă factura marcată drept respinsă e de fapt o factură **storno**, butonul „Trimite în SPV" nu apare deloc pentru ea — generatorul de XML din produs construiește azi doar facturi de tip standard (cod 380), nu și tipul specific de stornare/notă de credit (cod 381). O factură storno nu poate fi retransmisă prin acest ecran, indiferent de motivul respingerii inițiale.

Dacă o trimitere e deja activă pentru aceeași factură (încărcată sau în procesare la ANAF), o a doua retransmitere e blocată intenționat — upload-ul la ANAF nu e o operațiune sigură de repetat, iar o dublă trimitere ar produce o factură dublă în sistemul național.

## Ce se greșește în practică

- Se așteaptă ca o factură cu eroare de încărcare să fie retrimisă automat, la fel ca urmărirea recipisei — urmărirea unei trimiteri deja făcute e automată, dar declanșarea unei noi trimiteri nu e.
- Se încearcă retransmiterea unei facturi storno din ecranul obișnuit, fără să se știe că butonul lipsește deliberat pentru acest tip de document.
- Se corectează factura fără să se citească mesajul exact de eroare al validatorului, riscând să se repete aceeași greșeală la retrimitere.

## Ce face iConta.eu

Nu trimite nimic ce nu a trecut întâi de validatorul public ANAF, iar la eșec arată mesajele exacte de eroare, ca să corectezi înainte de a retrimite. Nu reîncearcă singur nicio trimitere eșuată — fiecare retransmitere e o acțiune manuală, per factură, cu protecție împotriva dublei trimiteri. Pentru facturile storno, spunem direct: azi acest flux nu e susținut din ecranul de facturi, ca să nu lase impresia unei funcții care nu produce rezultatul așteptat.

[iConta.eu](/)
