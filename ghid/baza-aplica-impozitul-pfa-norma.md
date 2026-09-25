---
title: "La ce bază se aplică impozitul pentru PFA la normă de venit?"
description: "Impozitul de 10% se aplică direct pe norma anuală de venit ajustată (eventual redusă proporțional) — fără nicio deducere de CAS sau CASS din bază, spre deosebire de sistemul real."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# La ce bază se aplică impozitul pentru PFA la normă de venit?

La normă de venit, baza impozabilă nu are nicio legătură cu banii efectiv încasați în cont sau în numerar în anul respectiv — e o valoare fixă, publicată de direcția regională a finanțelor publice, pe care legea o impozitează direct cu 10%, fără să scadă din ea contribuțiile sociale.

## Temeiul legal

::: ghid-temei
„Contribuabilii care realizează venituri din activități independente pentru care venitul net anual se stabilește pe baza normelor de venit au obligația stabilirii impozitului anual datorat, pe baza Declarației unice privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice prin aplicarea cotei de 10% asupra normei anuale de venit ajustate, după caz."
— Codul fiscal (Legea 227/2015), art. 69^2 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„În cazul contribuabililor care realizează venituri din activități independente, altele decât venituri din profesii liberale definite la art. 67 alin. (2), venitul net anual se determină pe baza normelor de venit de la locul desfășurării activității."
— Codul fiscal, art. 69 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce compune baza impozabilă:

- Punctul de plecare e norma de venit anuală, publicată pentru activitatea CAEN și locul de desfășurare (art. 69 alin. (1)-(2)), nu poate fi mai mică decât 12 salarii minime brute pe țară (art. 69 alin. (3)).
- Norma poate fi ajustată de contribuabil cu coeficienții de corecție publicați de DGRFP (art. 69 alin. (10)) și se reduce proporțional dacă activitatea nu s-a desfășurat un an calendaristic întreg (art. 69 alin. (5)).
- Impozitul de 10% se aplică DIRECT pe norma astfel stabilită (ajustată/redusă), fără nicio deducere a CAS și CASS din bază (art. 69^2 alin. (1)) — regulă distinctă de sistemul real, unde impozitul se aplică pe venitul net rămas după scăderea CAS și CASS datorate (art. 118 alin. (2) lit. b), aplicabil doar veniturilor determinate în sistem real, nu celor la normă).
- Dacă în cursul anului venitul brut efectiv realizat depășește 25.000 euro, din anul următor contribuabilul trece obligatoriu la sistem real (art. 69 alin. (9)) — de atunci, baza redevine venit brut minus cheltuieli deductibile, iar impozitul se calculează potrivit art. 118 și art. 123 alin. (1), cu deducerea CAS/CASS.

## Ce se greșește în practică

- Se scad CAS și CASS din norma de venit înainte de a aplica impozitul de 10%, prin analogie cu sistemul real — regula specifică normei de venit (art. 69^2 alin. (1)) nu prevede această deducere; impozitul se aplică direct pe norma ajustată.
- Se ignoră reducerea proporțională a normei pentru activitatea desfășurată doar o parte din an, calculând impozitul pe norma întreagă.
- Se calculează impozitul pe încasările efective ale anului, confundând norma de venit (fixă) cu sistemul real (venit brut minus cheltuieli).

## Ce face iConta.eu

Motorul `core/d212_engine.py` (funcția `calculeaza_d212`) implementează regula sistemului real (art. 118 alin. (2) lit. b) CF) — venit net, apoi CAS și CASS, apoi impozitul de 10% pe rest — pentru venitul net rezultat din venit brut minus cheltuieli deductibile înregistrate în Registrul-jurnal de încasări și plăți (`core/rip_api.py`, `fisa_d212`). Acest motor nu se aplică și normei de venit, unde formula legală e alta (art. 69^2 alin. (1): 10% direct pe norma ajustată, fără deducere de CAS/CASS).

Pentru normă de venit, aplicația nu calculează automat baza impozabilă: norma anuală, ajustarea cu coeficienți și reducerea proporțională pentru activitate parțială se introduc manual în declarație. Registrul de evidență fiscală (`core/registru_evidenta_fiscala.py`, OMFP 3254/2017) susține corect regula specifică — la normă de venit nu se înscriu cheltuieli deductibile — dar nu calculează impozitul propriu-zis.

[iConta.eu](/)
