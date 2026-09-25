---
title: "Ce este Declarația Unică D212 în 2026?"
description: "D212 este declarația prin care persoanele fizice își stabilesc singure impozitul pe venit și contribuțiile sociale (CAS, CASS) pentru veniturile realizate în afara salariului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce este Declarația Unică D212 în 2026?

Declarația unică privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice (D212) e formularul prin care o persoană fizică își autoimpune atât impozitul pe venit, cât și contribuțiile sociale (CAS și CASS), pentru veniturile realizate în afara salariului — activități independente, drepturi de proprietate intelectuală, cedarea folosinței bunurilor, investiții, activități agricole sau alte surse.

## Temeiul legal

::: ghid-temei
„Contribuabilii au obligația depunerii Declarației unice privind impozitul pe venit și contribuțiile sociale la organul fiscal competent, pentru fiecare an fiscal, în cazul în care realizează, individual sau într-o formă de asociere, venituri/pierderi, după caz, din următoarele categorii de venit: a) activități independente; b) drepturi de proprietate intelectuală; c) cedarea folosinței bunurilor; d) investiții; e) activități agricole, silvicultură și piscicultură; f) alte surse."
— Codul fiscal (Legea 227/2015), art. 122 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce anume face D212:

- Stabilește impozitul pe venit datorat pentru anul fiscal anterior (10% asupra venitului net anual impozabil, conform art. 123 alin. (1)).
- Stabilește contribuția de asigurări sociale (CAS), acolo unde e datorată sau aleasă opțional (art. 148-151).
- Stabilește contribuția de asigurări sociale de sănătate (CASS), pe aceleași principii de plafonare pe trepte de salarii minime (art. 170, 174, 180).
- Constituie ea însăși titlu de creanță fiscală (art. 122 alin. (9)) — nu mai e nevoie de o decizie de impunere separată din partea ANAF pentru sumele declarate.

## Ce se greșește în practică

- Se confundă D212 cu o simplă „declarație de venit estimat" — de fapt combină în același formular veniturile realizate anul trecut ȘI, dacă e cazul, opțiunile pentru anul curent (CAS/CASS opționale).
- Se crede că D212 privește doar PFA — de fapt se depune și pentru chirii, dividende, dobânzi peste anumite plafoane, drepturi de autor sau venituri din străinătate.
- Se ignoră faptul că declarația constituie titlu de creanță — o sumă declarată greșit nu așteaptă o verificare ANAF ca să devină exigibilă, ci e scadentă la termenul legal.

## Ce face iConta.eu

D212 e o declarație **manuală** în iConta.eu (`core/d212.py`): aplicația nu are registru de persoane fizice și nu deduce automat veniturile lor din contabilitatea firmei — toate datele (venituri, baze de calcul, CAS, CASS, impozit) se introduc direct, per capitol (sistem real, normă de venit, străinătate), respectând structura validată de ANAF (D212Validator, namespace v11).

Pentru contribuabilii care își țin evidența financiară în iConta.eu prin Registrul-jurnal de încasări și plăți (OMFP 170/2015), funcția `fisa_d212` din `core/rip_api.py` calculează automat venitul net, CAS și CASS pe baza operațiunilor validate — dar numai pentru veniturile anilor 2025 și 2026, singurii ale căror plafoane sunt verificate la sursă în aplicație.

[iConta.eu](/)
