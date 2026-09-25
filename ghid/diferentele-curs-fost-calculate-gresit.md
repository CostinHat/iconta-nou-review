---
title: "Ce fac dacă diferențele de curs au fost calculate greșit?"
description: "Cum se corectează o eroare de calcul la diferențele de curs valutar (665/765), în funcție de exercițiul financiar în care a fost făcută greșeala."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă diferențele de curs au fost calculate greșit?

Diferențele de curs valutar se recunosc lunar, la reevaluarea soldurilor în valută (creanțe, datorii, disponibilități), pe conturile 665 (cheltuieli) sau 765 (venituri). O eroare aici — curs greșit folosit, sold neevaluat, semn inversat — nu se corectează la fel indiferent de moment: contează dacă eroarea aparține exercițiului financiar curent sau unuia încheiat deja.

## Temeiul legal

::: ghid-temei
„67. - (1) Corectarea erorilor aferente exercițiului financiar curent se efectuează pe seama contului de profit și pierdere. (2) Corectarea erorilor semnificative aferente exercițiilor financiare precedente se efectuează pe seama rezultatului reportat (contul 1174 «Rezultatul reportat provenit din corectarea erorilor contabile»). (3) Erorile nesemnificative aferente exercițiilor financiare precedente se corectează, de asemenea, pe seama rezultatului reportat. Totuși, potrivit politicilor contabile aprobate, erorile nesemnificative pot fi corectate pe seama contului de profit și pierdere."
— OMFP nr. 1802/2014, Reglementări contabile, pct. 67 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Aplicat la diferențele de curs valutar greșit calculate:

- **Dacă eroarea a fost descoperită în același exercițiu financiar** în care a fost făcută (de exemplu greșeală la reevaluarea din luna trecută, corectată luna aceasta, în același an), corecția se face direct pe conturile de venituri/cheltuieli (665/766), prin stornare și reînregistrare corectă.
- **Dacă eroarea privește un exercițiu financiar deja încheiat** (situațiile financiare anuale au fost deja depuse), corecția nu se mai face pe 665/765, ci pe **contul 1174** „Rezultatul reportat provenit din corectarea erorilor contabile", pentru erorile semnificative — și, opțional conform politicii contabile, tot pe 1174 și pentru erorile nesemnificative.
- Reevaluarea propriu-zisă a soldurilor rămâne cea din pct. 316-322 ale reglementărilor: la fiecare lună, la cursul BNR din ultima zi bancară — deci o corecție presupune, în primul rând, verificarea cursului corect folosit inițial față de cel corect al BNR pentru data de referință.

## Ce se greșește în practică

- Se corectează diferențele de curs ale unui an financiar închis direct pe 665/765 din anul curent, ceea ce denaturează rezultatul curent, în loc să se folosească rezultatul reportat (1174), potrivit pct. 67 alin. (2)-(3).
- Se confundă pragul de semnificație — nu orice eroare mică se poate corecta pe profit și pierdere fără o analiză a impactului cumulat; legea cere evaluarea în context, ținând cont de natura și valoarea individuală sau cumulată a elementelor afectate.
- Se omite actualizarea notelor explicative la situațiile financiare, deși pct. 68 alin. (3) cere prezentarea naturii erorii constatate și a perioadelor afectate.

## Ce face iConta.eu

iConta.eu calculează diferențele de curs valutar (665/765) atât la decontarea creanțelor/datoriilor în valută, cât și la reevaluarea lunară a soldurilor, folosind cursul BNR al zilei introduse de utilizator — motorul intern refuză explicit să calculeze o diferență fără un curs declarat, tocmai pentru a evita o valoare implicită tăcută care ar putea deveni greșită la schimbarea legii sau a cursului. Dacă o diferență a fost deja înregistrată cu un curs greșit, corectarea ei — inclusiv decizia dacă se stornează pe 665/765 curent sau se trece pe rezultatul reportat (1174), pentru exerciții închise — rămâne o decizie manuală a contabilului, aplicația nu identifică automat erorile de curs deja înregistrate.

[iConta.eu](/)
