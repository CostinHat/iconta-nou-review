---
title: "Cum obțin acces SPV pentru o firmă nouă?"
description: "Regulile OMFP 660/2017 pentru înregistrarea unei persoane juridice ca utilizator SPV — prin reprezentant legal, reprezentant desemnat sau împuternicit — și ce înregistrează efectiv iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum obțin acces SPV pentru o firmă nouă?

Spațiul Privat Virtual (SPV) e canalul obligatoriu de comunicare electronică cu ANAF. Pentru o firmă nou-înființată, accesul se obține fie direct de administrator (cu certificat digital calificat pe numele lui sau al firmei), fie printr-un împuternicit — de regulă contabilul sau cabinetul de contabilitate care gestionează relația cu ANAF.

## Temeiul legal

::: ghid-temei
„(1) Persoanele juridice sau alte entităţi fără personalitate juridică se pot identifica în mediul electronic astfel: a) cu certificatul calificat al persoanei juridice sau al entităţii fără personalitate juridică; b) cu certificatul calificat deţinut de persoana fizică reprezentant legal al persoanei juridice [...]; c) cu certificatul calificat deţinut de reprezentantul desemnat al persoanei juridice [...]; d) cu certificatul calificat deţinut de împuternicitul persoanei juridice [...]. [...] (6) În scopul accesului la SPV, persoanele fizice, persoanele juridice sau alte entităţi fără personalitate juridică pot desemna un împuternicit în condiţiile art. 18 din Codul de procedură fiscală."
— OMFP 660/2017, art. 15 alin. (1) și (6) (sursă: anaf_surse/omfp_660_2017.txt)
:::

Pașii practici pentru o firmă nouă:

- Administratorul (reprezentantul legal) trebuie să dețină un certificat digital calificat, emis de un furnizor acreditat conform Regulamentului (UE) 910/2014, pe numele lui sau al firmei.
- Cererea de înregistrare ca utilizator SPV se depune electronic, prin platforma dedicată, cu datele de identificare ale firmei, calitatea solicitantului și un număr de telefon mobil valid (art. 16).
- Firma poate alege să delege accesul unui **împuternicit** (de regulă contabilul), caz în care împuternicirea trebuie să fie generală pentru toate operațiunile din SPV și să conțină acordul privind accesul la istoricul acțiunilor anterioare (art. 15 alin. (9)).
- Ori de câte ori se schimbă administratorul sau reprezentantul desemnat, noul reprezentant trebuie să înregistreze de îndată accesul propriu și să radieze accesul persoanei înlocuite (art. 15 alin. (5)) — accesul SPV nu se transferă automat.

## Ce se greșește în practică

- Se așteaptă ca SPV-ul să fie activ automat de la înființarea firmei — înregistrarea e o cerere separată, depusă electronic, care necesită deja un certificat digital calificat valid.
- Se confundă certificatul digital al administratorului (persoană fizică) cu unul emis pe firmă — oricare dintre cele patru variante e valabilă (art. 15 alin. (1)), dar trebuie ales și configurat explicit la înregistrare.
- La schimbarea administratorului, se lasă vechiul cont SPV activ „ca să nu se piardă istoricul" — legea cere radierea persoanei schimbate odată cu înregistrarea noului reprezentant.

## Ce face iConta.eu

iConta.eu are un conector SPV real, pe bază de OAuth2 cu certificat digital: aplicația gestionează autorizarea, stochează tokenul de acces criptat și îl reînnoiește automat (cu rotația impusă de ANAF la fiecare refresh). Conectorul presupune însă că firma (sau cabinetul care o reprezintă) **are deja acces SPV activ**, obținut conform procedurii OMFP 660/2017 — iConta.eu nu depune cererea inițială de înregistrare ca utilizator SPV și nu înlocuiește pașii de identificare electronică descriși mai sus; el preia și folosește accesul odată ce acesta există.

[iConta.eu](/)
