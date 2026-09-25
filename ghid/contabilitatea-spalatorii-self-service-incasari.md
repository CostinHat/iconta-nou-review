---
title: "Contabilitatea unei spălătorii self-service: încasări"
description: "Obligația de a utiliza aparate de marcat electronice fiscale pentru încasările de la o spălătorie self-service, indiferent dacă plata se face cu numerar sau card."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Contabilitatea unei spălătorii self-service: încasări

O spălătorie auto sau de rufe self-service încasează de la persoane fizice, adesea prin automate cu monede, fise sau card. Legea tratează aceste încasări exact ca orice altă vânzare cu amănuntul către populație — cu obligația de bon fiscal.

## Temeiul legal

::: ghid-temei
„Operatorii economici care încasează, integral sau parțial, cu numerar sau prin utilizarea cardurilor de credit/debit sau a substitutelor de numerar contravaloarea bunurilor livrate cu amănuntul, precum și a prestărilor de servicii efectuate direct către populație sunt obligați să utilizeze aparate de marcat electronice fiscale."
— Ordonanța de urgență a Guvernului nr. 28/1999, art. 1 alin. (1) (sursă: anaf_surse/oug_28_1999.html)
:::

Ce rezultă pentru o spălătorie self-service:

- Serviciul de spălătorie prestat direct către persoane fizice se încadrează la obligația generală de utilizare a aparatelor de marcat electronice fiscale — indiferent dacă plata se face cu numerar, cu cardul sau printr-un alt substitut de numerar (fise, monede-jeton).
- Bonul fiscal trebuie emis și înmânat clientului la momentul încasării, cu excepția plăților exclusiv prin card, unde legea nu mai impune tipărirea/înmânarea automată a bonului (extrasul de cont ține locul lui ca mijloc de probă), dar clientul poate cere oricând bonul.
- Legea prevede o listă limitativă de activități exceptate de la obligația casei de marcat (de exemplu vânzarea pe bază de bonuri cu valoare fixă tipărite conform legii, anumite servicii financiare) — o spălătorie self-service nu se regăsește printre aceste excepții.

## Ce se greșește în practică

- Se presupune că automatele self-service (fără casier prezent) sunt exceptate de la obligația de casă de marcat fiscală doar pentru că nu există interacțiune umană directă la momentul plății.
- Se emite bon fiscal doar pentru încasările în numerar, ignorând obligația și pentru plățile cu cardul acolo unde clientul solicită explicit bonul.
- Se contabilizează încasările global, la sfârșit de lună, din extrasul de cont, fără susținerea rapoartelor Z zilnice emise de aparatul de marcat fiscal.

## Ce face iConta.eu

iConta.eu importă Raportul Z emis de casa de marcat (AMEF), în format .p7b sau XML, structurat conform OPANAF 146/2018: extrage totalurile zilei pe cote de TVA și pe tipuri de plată (card, numerar, tichete), din care construiește automat nota contabilă zilnică a încasărilor. Această funcționalitate e live pentru firmele care folosesc case de marcat electronice fiscale conectate la fluxul de raportare standard — inclusiv pentru comerț cu amănuntul și HoReCa. Aplicația nu emite ea însăși bonuri fiscale și nu înlocuiește obligația legală de a dota punctele de încasare (inclusiv echipamentele self-service) cu aparate de marcat electronice fiscale conforme; ea preia și contabilizează datele deja generate de aceste aparate.

[iConta.eu](/)
