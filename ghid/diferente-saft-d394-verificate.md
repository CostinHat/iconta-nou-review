---
title: "Ce diferențe între SAF-T și D394 trebuie verificate?"
description: "SAF-T (D406) și D394 nu raportează același lucru — D394 e o subselecție de tranzacții pe TVA, SAF-T e întreaga evidență contabilă. Ce merită comparat între ele."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce diferențe între SAF-T și D394 trebuie verificate?

D394 și fișierul standard de control fiscal (SAF-T, depus prin declarația D406) au surse comune de date, dar domenii complet diferite ca întindere. D394 raportează doar un subset de tranzacții relevante pentru TVA cu parteneri naționali; SAF-T raportează întreaga evidență contabilă și fiscală a firmei, la un nivel de detaliu mult mai mare.

## Temeiul legal

::: ghid-temei
„Natura informaţiilor pe care contribuabilul/plătitorul trebuie să le declare prin fişierul standard de control fiscal (SAF-T) este prevăzută în anexa nr. 1. [...] Fişierul standard de control fiscal (SAF-T) se transmite de către contribuabili/plătitori prin intermediul Declaraţiei informative privind fişierul standard de control fiscal, denumită în continuare Declaraţia informativă D406, al cărei model este prevăzut în anexa nr. 2."
— OPANAF 1783/2021, art. 1-2 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)

„Persoanele impozabile înregistrate în scopuri de TVA în România sunt obligate să declare livrările de bunuri, prestările de servicii şi achiziţiile de bunuri şi servicii realizate pe teritoriul României către/de la orice persoană, aşa cum este definită la art. 266 alin. (1) pct. 24 din Legea nr. 227/2015 privind Codul fiscal, cu modificările şi completările ulterioare."
— OPANAF 3769/2015, art. 1 (sursă: anaf_surse/opanaf_3769_2015_d394_baza.txt)
:::

Cele două declarații au baze legale, obligații și conținut diferite:

- **D394** e o declarație informativă, cu bază legală proprie (OPANAF 3769/2015, actualizat prin OPANAF 2194/2025), care raportează livrările, prestările și achizițiile pe teritoriul național, defalcate pe cote de TVA și pe partener.
- **SAF-T/D406** are bază legală separată (art. 59^1 din Codul de procedură fiscală și OPANAF 1783/2021), obligativitatea fiind stabilită pe categorii de contribuabili (mari, mijlocii, mici) cu date de intrare diferite, nu de înregistrarea TVA în sine.
- SAF-T include secțiuni pe care D394 nu le atinge deloc: planul de conturi, jurnalul contabil (notele contabile), mijloacele fixe, stocurile — D394 se limitează la operațiunile relevante pentru TVA.
- Fereastra de raportare a celor două poate diferi ca structură (lună calendaristică versus perioadă fiscală de TVA), motiv pentru care alinierea corectă a intervalelor raportate merită verificată separat pentru fiecare firmă, mai ales la cei cu perioadă fiscală trimestrială.

## Ce se greșește în practică

- Se presupune că SAF-T „conține" D394 și că, dacă unul e corect, celălalt e implicit corect — sunt generate din surse comune, dar cu logică de agregare diferită, așa că o eroare poate apărea în unul fără să apară în celălalt.
- Se compară cifre agregate (total baza de TVA din D394 cu totalul facturilor din SAF-T) fără să se țină cont că SAF-T include și operațiuni fără relevanță pentru D394 (de exemplu operațiuni fără parteneri naționali relevanți sau documente fără impact TVA).
- Se ignoră faptul că fereastra de timp acoperită de cele două declarații trebuie aliniată pe aceeași perioadă fiscală de TVA a firmei — nu pe luna calendaristică implicită.

## Ce face iConta.eu

Fereastra de date a SAF-T-ului urmează explicit perioada fiscală declarată pentru TVA a firmei (lunar sau trimestrial), nu doar luna-ancoră — o reparație aplicată de curând tocmai pentru ca SAF-T-ul unei firme trimestriale să conțină toate lunile perioadei, la fel ca D300 și D394 pentru același trimestru, nu doar o singură lună din trei.

Aplicația nu are, la data acestui ghid, un modul dedicat de comparație automată între D394 și SAF-T — cele două sunt generatoare separate (`d394.py`, respectiv `d406.py`), cu propriile reguli de calcul, propriile validări locale pe validatorul oficial ANAF și propriile avertismente pentru date incomplete sau conturi neîncadrate în planul de conturi declarat. O verificare încrucișată punctuală, cifră cu cifră, între cele două rămâne o operațiune manuală a contabilului.

[iConta.eu](/)
