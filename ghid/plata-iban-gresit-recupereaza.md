---
title: "Plată către un IBAN greșit: cum se recuperează"
description: iConta.eu previne, prin validare IBAN, transmiterea greșită a banilor la plata salariilor — dar nu are nicio funcție de recuperare a unei plăți deja trimise către un IBAN greșit. Recuperarea e un proces bancar/civil, în afara aplicației.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Plată către un IBAN greșit: cum se recuperează

Dacă ai transmis deja o plată către un IBAN greșit, recuperarea ei nu se întâmplă în nicio aplicație de contabilitate — inclusiv iConta.eu — ci prin banca ta și, dacă e necesar, pe cale civilă. Explicăm mai jos ce poți face practic și, separat, ce face (și ce nu face) iConta.eu pentru a preveni astfel de situații.

## Temeiul legal

Nu am identificat, în dosarul verificat pentru acest ghid, un text de lege românesc specific procedurii de recuperare a unei plăți transmise către un IBAN greșit — subiectul ține de relația ta cu banca emitentă și, eventual, cu banca destinatarului, și, dacă aceasta nu cooperează voluntar, de dreptul civil general. Nu redăm aici un articol anume, ca să nu riscăm o citare neverificată.

## Ce poți face, practic

- **Contactează imediat banca ta** (cea de la care ai inițiat plata) și solicită inițierea unei cereri de recuperare/retragere a fondurilor. Șansele de reușită scad rapid cu timpul, mai ales dacă banii au fost deja retrași de titularul contului destinatar.
- Dacă banca destinatară sau titularul contului nu cooperează, stabilirea demersului corect (notificare, mediere, acțiune în instanță) trebuie făcută cu un consultant juridic, nu pe baza unui ghid general — situația fiecărui caz depinde de detalii (sumă, cont, timp scurs) pe care nu le putem generaliza aici.
- Păstrează toate dovezile operațiunii (ordin de plată, extras de cont, confirmarea băncii) — sunt necesare la orice demers ulterior.

## Ce se greșește în practică

Se presupune că banca poate „anula" automat o plată deja executată, ca și cum ar fi o simplă eroare tehnică reversibilă. În realitate, odată ce fondurile au ajuns și au fost creditate în contul destinatarului, recuperarea depinde de cooperarea voluntară a acestuia (sau a băncii lui) — banca inițiatoare nu poate retrage unilateral banii dintr-un cont care nu-i aparține.

## Ce face iConta.eu

iConta.eu nu are nicio funcționalitate de recuperare a unei plăți deja transmise — nici pentru salarii, nici pentru alt tip de plată. Ce are, în schimb, e o componentă de **prevenție**: la generarea fișierului de plată a salariilor (fișierul SEPA pentru NET-ul salarial), aplicația validează fiecare IBAN introdus pentru angajați (verificare mod-97, standard IBAN) și exclude din fișier orice angajat fără un IBAN valid, raportându-l separat, astfel încât fișierul de plată să nu fie generat cu un IBAN eronat pentru salariați. Această validare acoperă exclusiv acest flux, la momentul introducerii datelor — nu oferă și nu poate oferi o soluție pentru o plată deja executată, indiferent de canalul prin care a fost făcută.

[iConta.eu](/)
