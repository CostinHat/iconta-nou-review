---
title: "Poate o întreprindere individuală să fie la normă de venit?"
description: "Codul fiscal nu diferențiază PFA de întreprinderea individuală (II) la stabilirea venitului net pe bază de normă de venit — condiția e activitatea, nu forma de organizare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Poate o întreprindere individuală să fie la normă de venit?

Da. Din perspectiva impozitului pe venit, Codul fiscal tratează la fel PFA, întreprinderea individuală (II) și întreprinderea familială (IF) — toate sunt „activități independente" desfășurate individual, indiferent de forma de organizare aleasă la înființare potrivit OUG 44/2008. Norma de venit se leagă de **activitatea CAEN** desfășurată, nu de eticheta juridică a titularului.

## Temeiul legal

::: ghid-temei
„Veniturile din activități independente cuprind veniturile din activități de producție, comerț, prestări de servicii și veniturile din profesii liberale, realizate în mod individual și/sau într-o formă de asociere, inclusiv din activități adiacente."
— Codul fiscal (Legea 227/2015), art. 67 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„În cazul contribuabililor care realizează venituri din activități independente, altele decât venituri din profesii liberale definite la art. 67 alin. (2), venitul net anual se determină pe baza normelor de venit de la locul desfășurării activității."
— Codul fiscal, art. 69 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă de aici pentru o II:

- Art. 67 alin. (1) nu condiționează încadrarea în „activități independente" de forma juridică — PFA și II intră amândouă aici, atâta timp cât activitatea se desfășoară individual.
- Art. 69 alin. (1) leagă norma de venit de **locul desfășurării activității** și de nomenclatorul MFP al activităților eligibile (art. 69 alin. (2)), nu de forma de organizare a titularului.
- Condiția reală de eligibilitate: activitatea CAEN concretă să fie inclusă în nomenclatorul stabilit anual de direcțiile generale regionale ale finanțelor publice (art. 69 alin. (2) lit. a) și b)).
- Dacă venitul brut anual din anul anterior depășește echivalentul a 25.000 euro, contribuabilul — indiferent că e PFA sau II — trece obligatoriu la sistem real din anul următor (art. 69 alin. (9)).

## Ce se greșește în practică

- Se presupune că norma de venit e un regim „doar pentru PFA", iar întreprinderea individuală ar fi automat obligată la sistem real — nu există un asemenea temei în Codul fiscal.
- Se verifică forma de organizare în loc să se verifice codul CAEN al activității în nomenclatorul publicat de DGRFP pentru anul respectiv.
- Se ignoră pragul de 25.000 euro venit brut anual, care obligă trecerea la sistem real din anul următor, indiferent de formă.

## Ce face iConta.eu

Generatorul D212 al iConta.eu (`core/d212.py`) emite capitolul de normă de venit (`cap12`) cu câmpul `norma_forma_org`, care înregistrează forma de organizare a titularului — inclusiv II — exact cum cere structura validată de ANAF (D212Validator). Registrul de evidență fiscală pentru persoane fizice (varianta „venituri_pf", conform OMFP 3254/2017, `core/registru_evidenta_fiscala.py`) susține de asemenea modul „normă de venit" (`mod_venit_net = 3`) ca opțiune de completare a evidenței, fără să facă vreo distincție între PFA și II la validarea înregistrării.

Ce nu face aplicația: nu verifică dacă activitatea CAEN concretă e inclusă în nomenclatorul de normă de venit publicat de DGRFP pentru anul de raportare — nomenclatorul nu e un cod fiscal fix, ci un document regional actualizat anual, iar verificarea eligibilității rămâne responsabilitatea contabilului.

[iConta.eu](/)
