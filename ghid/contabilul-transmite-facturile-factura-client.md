---
title: "Poate contabilul transmite facturile în e-Factura pentru client?"
description: Da — legal, prin calitatea de reprezentant desemnat sau împuternicit în SPV; tehnic, prin certificatul calificat al contabilului, conectat o singură dată per cabinet. Explicăm ambele fețe ale răspunsului.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Poate contabilul transmite facturile în e-Factura pentru client?

Da. Este exact scenariul obișnuit pentru firmele care lucrează cu un cabinet de contabilitate: contabilul, nu clientul, este cel care transmite efectiv facturile în RO e-Factura, folosind propriul certificat digital calificat. Răspunsul are însă două fețe — una legală (cu ce calitate poate face asta contabilul) și una tehnică (cum funcționează, concret, conexiunea).

## Temeiul legal

::: ghid-temei
„SPV este accesibil persoanei juridice sau entității fără personalitate juridică prin reprezentat legal, prin reprezentant desemnat sau prin împuternicit." — OMFP nr. 660/2017 privind aprobarea Procedurii de comunicare prin mijloace electronice de transmitere la distanță, art. 23 alin. (2)
:::

Legea prevede explicit calitatea de **împuternicit** ca una dintre căile prin care o persoană juridică poate avea acces la SPV — și, prin extensie, la transmiterea facturilor prin RO e-Factura. Condiția-cheie (art. 15 alin. 9 din același ordin): împuternicirea trebuie să fie **generală**, pentru toate operațiunile din SPV, cu acord de acces la istoricul acțiunilor anterioare ale firmei reprezentate — nu o împuternicire limitată doar la „transmiterea facturilor".

## Cum funcționează tehnic, în spatele acestei calități legale

Din perspectiva conexiunii SPV folosite de o aplicație precum iConta.eu, autorizarea OAuth cu ANAF se face **o singură dată, per cabinet**, cu certificatul calificat al contabilului — nu separat, pentru fiecare client în parte. Odată ce certificatul contabilului are drept SPV recunoscut pe CIF-ul unei firme (ca reprezentant legal, reprezentant desemnat sau împuternicit, conform art. 15), toate facturile clienților ale căror CIF-uri sunt acoperite de acel drept pot fi transmise prin aceeași conexiune, fără o autorizare tehnică separată pentru fiecare firmă.

Important: verificarea faptului că certificatul contabilului *chiar are* drept pe un CIF anume nu se vede direct în token-ul de autorizare — se confirmă empiric, la fiecare cerere către un CIF, prin răspunsul primit de la ANAF. Dacă certificatul nu are dreptul respectiv, transmiterea pentru acel client eșuează, indiferent că restul conexiunii funcționează normal pentru alți clienți.

## Ce se greșește în practică

- Se presupune că fiecare client trebuie să aibă propriul cont/conexiune SPV separată în aplicație pentru ca facturile lui să poată fi transmise — de fapt, conexiunea e a cabinetului, nu a fiecărei firme.
- Se confundă „contabilul poate transmite facturile" cu „contabilul are automat drept pe orice CIF nou preluat" — dreptul SPV pe un CIF anume trebuie obținut/confirmat separat la ANAF (împuternicire generală conform art. 15), nu se moștenește automat prin simpla adăugare a firmei ca și client în aplicație.
- Se acceptă o împuternicire parțială („doar pentru facturi"), crezând că e suficientă — art. 17 alin. (5) prevede explicit respingerea cererii dacă împuternicirea nu e generală, pentru toate operațiunile din SPV.

## Ce face iConta.eu

Conectarea la SPV/e-Factura se face o dată, la nivel de cabinet, cu certificatul calificat al contabilului. Odată realizată, toate firmele-client pentru care certificatul are drept SPV recunoscut de ANAF pot avea facturile transmise prin aceeași conexiune, fără o reautorizare separată per client. Dacă dreptul pe un CIF anume lipsește, aplicația primește acest lucru direct din răspunsul ANAF la cererea respectivă — nu e o presupunere sau o stare configurată manual în iConta.eu.

[iConta.eu](/)
