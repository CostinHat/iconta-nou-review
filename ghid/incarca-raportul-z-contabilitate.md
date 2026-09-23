---
title: Cum se încarcă raportul Z în contabilitate
description: Raportul Z zilnic al casei de marcat intră în contabilitate fie prin importul fișierului AMEF (p7b/XML), fie introdus manual — cele două căi produc note diferite ca statut. Vezi ce face fiecare.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se încarcă raportul Z în contabilitate

Raportul Z e documentul emis zilnic de casa de marcat electronică fiscală (AMEF) la închiderea zilei fiscale — totalul încasărilor, pe cote de TVA și pe tipuri de plată. În contabilitate intră printr-una din cele două căi disponibile pe ecranul „Raport Z", nu automat.

## Temeiul legal

::: ghid-temei
„conțin datele aferente fiecărei zile fiscale încheiate" — OPANAF 146/2018 (norma metodologică pentru aplicarea OUG 28/1999 privind obligația operatorilor economici de a utiliza aparate de marcat electronice fiscale), descrierea rapoartelor de la secțiunile II.1-II.7 ale anexei 2
:::

## Cele două căi de încărcare

**1. Import fișier AMEF (p7b sau XML).** Se încarcă direct fișierul generat de casa de marcat. Aplicația citește secțiunea `<rB>` a mesajului — totalurile pe fiecare cotă de TVA din `<coteZ>` (nu doar 11%/21%, orice cotă apărută efectiv în fișier) și plățile pe tip din `<pl>` (card, numerar, tichete etc., conform nomenclatorului OPANAF 146/2018). Nota contabilă rezultată are statut **ciornă** — așteaptă o verificare separată înainte de a intra în rulaj.

**2. Introducere manuală.** Se completează Data, NUI-ul casei de marcat, numărul raportului, totalurile pe cele două cote (11% mâncare / 21% alcool și sucuri), numerarul și cardul. Aplicația calculează TVA prin „sută mărită" (`total × cotă / (100+cotă)`) și generează nota direct **ca validată**, fără pasul intermediar de ciornă.

Ambele căi scriu aceleași conturi: `5311 = 707` pentru numerar, `5125 = 707` pentru card (și orice altă plată electronică din nomenclator), `707 = 4427` pentru TVA colectată pe fiecare cotă.

Cheia care ține unicitatea raportului e combinația **NUI casă de marcat + număr raport Z** — nu data calendaristică. La un al doilea import cu aceeași combinație, aplicația refuză duplicarea și arată nota existentă.

## Ce se greșește în practică

Cea mai frecventă greșeală e introducerea manuală repetată a aceluiași Z (de exemplu după o eroare de calcul), fără să se verifice întâi dacă nota există deja — combinația NUI+număr o va respinge, dar mesajul de eroare trebuie citit, nu ocolit prin schimbarea numărului. A doua: tratarea căii manuale ca fiind la fel de sigură ca importul — nota manuală e validată direct, deci orice greșeală de tastare a totalurilor ajunge direct în rulaj, nu într-o ciornă verificabilă.

## Ce face iConta.eu

Ecranul „Raport Z" oferă ambele căi pe același formular. Importul de fișier apelează parserul propriu pentru structura AMEF (`core/amef_import.py`) și generează o notă ciornă (`repo_contabilitate.nota_amef_ciorna`); introducerea manuală (`core/uc_tenants.py`, funcția `horeca_raport_z`) validează matematic totalurile (numerar+card = total pe cote) și generează nota direct ca validată. Unicitatea pe NUI+număr e impusă și la nivel de bază de date, printr-un index unic — nu doar prin verificarea din aplicație.

[iConta.eu](/)
