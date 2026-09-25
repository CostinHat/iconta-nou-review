---
title: "Cum înregistrez decontul administratorului fără avans acordat anterior?"
description: "Documentul justificativ folosit când administratorul plătește din bani proprii cheltuieli ale firmei, fără să fi primit un avans spre decontare în prealabil."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum înregistrez decontul administratorului fără avans acordat anterior?

Situația e frecventă la firmele mici: administratorul plătește din buzunarul propriu o cheltuială a firmei (o factură urgentă, un abonament, o taxă), fără să fi ridicat înainte un avans spre decontare din casierie. Contabil, asta nu e „decontare de avans" în sensul strict al termenului — pentru că nu a existat avans — ci o rambursare directă către administrator, iar documentul justificativ folosit e altul.

## Temeiul legal

```
::: ghid-temei
„DISPOZIȚIE DE PLATĂ/ÎNCASARE CĂTRE CASIERIE (Cod 14-4-4) Dispoziția de plată/încasare către casierie servește ca: - dispoziție pentru casierie, în vederea achitării în numerar a unor sume, potrivit dispozițiilor legale, inclusiv a avansurilor aprobate pentru cheltuieli de deplasare, precum și a diferenței de încasat de către titularul de avans în cazul justificării unor sume mai mari decât avansul primit, pentru procurare de materiale etc. [...] document justificativ de înregistrare în Registrul de casă și în contabilitate, în cazul plăților în numerar efectuate fără alt document justificativ."
— OMFP nr. 2.634/2015 privind documentele financiar-contabile, anexa 2 (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::
```

Ce rezultă din text pentru cazul administratorului fără avans prealabil:

- **Documentul justificativ potrivit este „Dispoziția de plată/încasare către casierie" (cod 14-4-4)** — norma îl descrie explicit pentru „diferența de încasat de către titularul de avans în cazul justificării unor sume mai mari decât avansul primit", ceea ce acoperă exact și cazul extrem în care avansul inițial a fost zero, iar toată suma cheltuită de administrator trebuie recuperată.
- Documentul funcționează ca **justificativ de plată în numerar fără alt document**, deci se poate folosi și când nu există în prealabil o „dispoziție de plată a avansului" — cheltuiala e recunoscută pe baza facturii/bonului plătit de administrator, iar dispoziția servește la rambursarea efectivă a banilor lui.
- Rambursarea se înregistrează prin **Registrul de casă**, ca orice altă plată în numerar — documentul stă la baza înregistrării atât în registru, cât și în contabilitate.

## Ce se greșește în practică

- Se așteaptă, greșit, ca administratorul să primească întâi un avans „formal", chiar și de valoare mică, doar ca să existe o mișcare de avans în evidență, deși norma permite decontarea directă a sumei plătite, fără avans prealabil.
- Se înregistrează cheltuiala pe cheltuieli, dar se omite documentul de rambursare efectivă către administrator, lăsând o sumă „pierdută" în evidența de casă.
- Se confundă rambursarea directă (fără avans) cu un împrumut al administratorului către firmă, tratat greșit prin cont de asociați/acționari, deși e vorba de o simplă plată a unei cheltuieli deja a firmei, în numele acesteia.

## Ce face iConta.eu

Modulul `core/casa.py` are funcțiile `avans_acordare`, `avans_deconteaza` și `avans_sold`, care calculează soldul rămas la decontarea unui avans (inclusiv, matematic, cazul în care suma justificată depășește avansul primit — rezultatul `rest_de_restituit` devine negativ, semn că firma datorează administratorului diferența). Din verificarea codului, funcția `avans_deconteaza` **presupune totuși un avans de plecare** (chiar și zero) și **nu generează automat** nota contabilă de rambursare efectivă a diferenței către administrator — acest ultim pas rămâne, la acest moment, o notă pe care contabilul o adaugă manual, folosind exact documentul „Dispoziție de plată către casierie" descris mai sus.

[iConta.eu](/)
