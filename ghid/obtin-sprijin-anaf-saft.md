---
title: "Cum obțin sprijin de la ANAF pentru SAF-T"
description: "Cele două forme oficiale de asistență pe care ANAF le pune la dispoziție contribuabililor pentru pregătirea și transmiterea fișierului standard de control fiscal (SAF-T/D406)."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum obțin sprijin de la ANAF pentru SAF-T

SAF-T (Standard Audit File for Tax), raportat prin Declarația informativă D406, e un fișier XML complex, generat din evidența contabilă și fiscală a firmei. Pentru contribuabilii care nu au un sistem ERP care să-l genereze automat, ANAF a pus la dispoziție instrumente concrete de sprijin — nu doar documentație, ci și un program de validare gratuit.

## Temeiul legal

::: ghid-temei
„Pentru pregătirea Declarației informative D406, ANAF pune la dispoziția contribuabilului/plătitorului două forme de asistență: a) specificațiile pentru formatul și conținutul Declarației informative D406; b) programul «Validator» pentru fișierul SAF-T în format XML - program independent, în format executabil, interpretat, scris în limbaj Java, cu care contribuabilii/plătitorii pot valida sintactic și în parte semantic raportarea, înainte de a o încărca pe portalul ANAF."
— OPANAF nr. 1783/2021, procedura de transmitere a fișierului SAF-T, pct. 2 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

- ANAF pune la dispoziție **specificațiile tehnice** pentru formatul și conținutul D406, publicate prin „Ghidul contribuabilului pentru pregătirea și depunerea Declarației informative D406".
- ANAF pune la dispoziție **programul Validator (Soft J)** — un executabil Java independent, care poate fi rulat local, la sediul contribuabilului, pentru verificarea sintactică și parțial semantică a fișierului XML, înainte de încărcarea efectivă pe portal.
- Există trei metode de lucru recunoscute oficial pentru pregătirea fișierului SAF-T: generare automată din sistemul informatic/ERP propriu, editare manuală pe schema SAF-T (pentru cei fără sistem contabil informatizat), sau generare externă printr-un operator de date specializat (pentru firmele cu servicii financiar-contabile externalizate).
- Declarația D406, sub formă de document PDF cu XML atașat, se generează automat de Validator după ce fișierul trece verificările.

## Ce se greșește în practică

- Se încarcă fișierul SAF-T direct pe portalul ANAF, fără validare locală prealabilă cu programul Validator, aflând abia acolo de erorile de structură.
- Se confundă validarea sintactică (structura fișierului) cu validarea semantică (corectitudinea datelor) — Validatorul acoperă doar parțial a doua categorie.
- Se ignoră „Ghidul contribuabilului" publicat de ANAF, care conține limitele și regulile de completare, și se merge doar după schema XSD brută.
- Firmele fără sistem ERP încearcă să genereze manual fișierul fără să folosească metoda de editare pe schema SAF-T recomandată oficial pentru acest caz.

## Ce face iConta.eu

Modulele `d406.py`, `d406_active.py` și `d406_reconciliere.py` din iConta.eu generează Declarația informativă D406 (SAF-T) și includ un mecanism intern de verificare independentă — o „balanță de rulaje" per cont, construită separat din înregistrările contabile brute, confruntată apoi cu totalurile din SAF-T-ul efectiv emis, cu blocare la orice dezechilibru. Această verificare internă e complementară programului Validator oficial al ANAF menționat mai sus, nu un înlocuitor al lui — folosirea Validatorului ANAF înainte de încărcarea pe portal rămâne recomandată, indiferent de softul folosit pentru generare.

[iConta.eu](/)
