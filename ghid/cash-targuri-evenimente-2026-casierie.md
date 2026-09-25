---
title: "Cash la târguri și evenimente 2026: casierie"
description: "O firmă care vinde cu numerar la un târg sau eveniment ocazional rămâne sub aceleași obligații de casă de marcat și plafon de numerar ca orice vânzare cu amănuntul, cu doar două excepții înguste."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cash la târguri și evenimente 2026: casierie

Caracterul temporar sau ocazional al unui stand de târg nu scutește, de regulă, de obligațiile fiscale legate de casierie. Legea prevede doar câteva excepții punctuale de la obligația de casă de marcat, iar plafonul de numerar de la persoane fizice se aplică neschimbat, indiferent de context.

## Temeiul legal

::: ghid-temei
„(1) Operatorii economici care încasează, integral sau parțial, cu numerar sau prin utilizarea cardurilor de credit/debit sau a substitutelor de numerar contravaloarea bunurilor livrate cu amănuntul, precum și a prestărilor de servicii efectuate direct către populație sunt obligați să utilizeze aparate de marcat electronice fiscale."
— OUG 28/1999 (republicată), art. 1 alin. (1) (sursă: anaf_surse/oug_28_1999.html)

„Se exceptează de la prevederile art. 1 alin. (1) încasările efectuate din următoarele activități: a) comerțul ocazional cu produse agricole din producție proprie efectuat de către producătorii agricoli individuali, autorizați în condițiile legii, în piețe, târguri, oboare sau în alte locuri publice autorizate; [...] d) activitățile pentru care încasările se realizează pe bază de bonuri cu valoare fixă tipărite conform legii - bilete de acces la spectacole, muzee, expoziții, târguri și oboare, grădini zoologice și grădini botanice, biblioteci, locuri de parcare pentru autovehicule, bilete de participare la jocuri de noroc și altele similare;"
— OUG 28/1999 (republicată), art. 2 lit. a) și d) (sursă: anaf_surse/oug_28_1999.html)

„Operațiunile de încasări în numerar efectuate de persoanele prevăzute la art. 1 alin. (1), de la persoane fizice, [...] precum și contravaloarea unor livrări de bunuri sau a unor prestări de servicii se efectuează în limita unui plafon zilnic de 10.000 lei de la o persoană."
— Legea 70/2015 (consolidată), art. 4 alin. (1) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

- Regula de bază: orice vânzare cu numerar către o persoană fizică, la un stand de târg sau eveniment, cere bon fiscal emis cu un aparat de marcat electronic fiscal — caracterul ocazional al vânzării nu contează.
- Excepția de la art. 2 lit. a) e îngustă: vizează exclusiv producătorii agricoli individuali autorizați, care vând produse din propria producție — nu o firmă sau un PFA care revinde produse cumpărate sau organizează standul altcuiva.
- Excepția de la art. 2 lit. d) (bilete tipărite cu valoare fixă la spectacole, expoziții, târguri) privește biletul de acces în sine, nu restul vânzărilor efectuate în interiorul evenimentului (produse, servicii suplimentare, consumații).
- Plafonul de 10.000 lei/zi de la aceeași persoană fizică (Legea 70/2015, art. 4 alin. (1)) se aplică neschimbat, inclusiv la un stand de târg — indiferent cât de aglomerată e ziua sau câte tranzacții se fac.

## Ce se greșește în practică

- Se presupune că vânzarea „ocazională", la un târg de câteva zile, scutește automat de obligația de casă de marcat — excepțiile din art. 2 sunt limitate strict la activitățile enumerate expres, nu la orice vânzare temporară.
- Se fragmentează încasările de la același client în cursul zilei de târg, ca să se rămână sub plafonul de 10.000 lei — interzis explicit de lege: plafonul se raportează la totalul zilnic încasat de la aceeași persoană, nu la fiecare tranzacție separat.
- Se confundă excepția pentru producători agricoli individuali cu orice vânzător prezent la un târg — excepția nu se extinde la comercianți care revând produse cumpărate sau la firme de catering/organizare de evenimente.

## Ce face iConta.eu

Modulul de casierie al iConta.eu (`core/casa.py`) urmărește plafoanele de numerar din Legea 70/2015, printre care plafonul zilnic de încasare de la o persoană fizică (10.000 lei), aplicat generic prin funcția `verifica_plafon()`, indiferent de contextul concret al vânzării — magazin, birou sau stand de eveniment/târg. Depășirea plafonului generează un avertisment (nivel „avertisment", nu o blocare a înregistrării), cu suma găsită și cea așteptată, pe fiecare zi și partener. Aplicația nu are însă nicio logică specifică pentru „vânzare la eveniment/târg" — nu distinge, de exemplu, un producător agricol individual exceptat de la obligația de AMEF (art. 2 lit. a)) de un comerciant obișnuit, și nu ține evidența biletelor tipărite cu valoare fixă de la art. 2 lit. d). Încadrarea corectă în aceste excepții rămâne integral responsabilitatea contabilului sau a firmei.

[iConta.eu](/)
