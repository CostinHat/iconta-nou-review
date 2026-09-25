---
title: "Cum corectez o încasare trecută de două ori în registrul de casă?"
description: "Regula din normele financiar-contabile pentru corectarea documentelor de casă: chitanțele și dispozițiile de încasare nu se corectează, ci se anulează sau se stornează."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum corectez o încasare trecută de două ori în registrul de casă?

O încasare înregistrată de două ori în registrul de casă nu se „corectează" prin ștergerea sau tăierea cifrei greșite, așa cum s-ar putea proceda la alte documente. Documentele de casă fac parte dintr-o categorie specială, pentru care normele contabile interzic explicit corectura directă.

## Temeiul legal

::: ghid-temei
„14. În documentele financiar-contabile nu sunt admise ștersături, modificări sau alte asemenea procedee [...] Erorile se corectează prin tăierea cu o linie a textului sau a cifrei greșite, concomitent înscriindu-se alături textul sau cifra corectă. [...]
15. În cazul documentelor financiar-contabile la care nu se admit corecturi, cum sunt cele pe baza cărora se primește, se eliberează sau se justifică numerarul, ori al altor documente pentru care normele de utilizare prevăd asemenea restricții, documentul întocmit greșit se anulează și se păstrează sau rămâne în carnetul respectiv. [...]
20. [...] În cazul stornărilor, pe documentul inițial se menționează numărul și data notei de contabilitate prin care s-a efectuat stornarea operațiunii, iar în nota de contabilitate de stornare se menționează documentul, data și numărul de ordine ale operațiunii care face obiectul stornării."
— OMFP 2634/2015, Anexa 1 (Norme generale), pct. 14, 15 și 20 (sursă: anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt)
:::

Pentru o încasare de casă dublată, rezultă două căi corecte, în funcție de momentul la care descoperiți greșeala:

- **Dacă documentul (chitanța/dispoziția de încasare) e încă needitat sau greșit întocmit chiar în acel moment**, pct. 15 cere anularea lui explicită — se scrie „ANULAT" pe exemplar, documentul rămâne în carnet, nu se distruge — și se emite un document nou, corect.
- **Dacă înregistrarea dublă a ajuns deja în evidența contabilă** (a doua încasare a fost deja înregistrată în registrul de casă și eventual reflectată în note contabile), corectarea se face prin **stornare**: o notă de contabilitate care anulează operațiunea greșită, cu referință explicită la documentul și numărul de ordine al operațiunii stornate — nu prin modificarea directă a sumei din registru.
- În ambele cazuri, soldul de casă trebuie să reflecte corect operațiunile reale — o simplă ștergere a rândului dublat, fără urmă documentară, încalcă cerința de trasabilitate de la pct. 14 și 15.

## Ce se greșește în practică

- Se șterge sau se modifică direct suma din registrul de casă, deși pct. 15 interzice explicit corecturile pe documentele de numerar — eroarea trebuie anulată sau stornată, nu editată.
- Se anulează documentul fizic dar nu se face nota de stornare corespunzătoare atunci când operațiunea dublă a ajuns deja în contabilitate — rămâne o discrepanță între document și înregistrare.
- Se pierde urma corecției: pct. 20 cere ca ambele documente (cel inițial și nota de stornare) să se refere reciproc, prin număr și dată — o corecție „mută", fără referință încrucișată, nu respectă norma.

## Ce face iConta.eu

Modulul de casierie al iConta.eu (`core/casa.py`) calculează soldul rulant al registrului de casă strict pe baza listei de operațiuni introduse (`registru_casa`), fără o funcție dedicată de „anulare" sau „stornare" a unei operațiuni — o încasare dublată trebuie eliminată sau contrabalansată manual de contabil, prin introducerea corecției ca operațiune nouă, cu urma ei documentară păstrată în afara aplicației. Aplicația verifică automat plafoanele de numerar (art. 4^2 din Legea 70/2015, inclusiv pragurile speciale pentru cash and carry) pe operațiunile introduse, dar nu semnalează dubluri de înregistrare și nu propune stornarea lor.

[iConta.eu](/)
