---
title: "Cum tratez fiscal amenzile ANAF?"
description: "Tratamentul contabil și fiscal al amenzilor, majorărilor și penalităților datorate autorităților: nedeductibile la impozitul pe profit, contul 6581."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum tratez fiscal amenzile ANAF?

O amendă primită de la ANAF (de exemplu pentru o contravenție constatată la control sau pentru nedepunerea la termen a unei declarații) e o cheltuială reală a firmei, dar tratamentul ei fiscal e clar: e **integral nedeductibilă** la calculul impozitului pe profit, spre deosebire de alte cheltuieli care doar au un plafon de deducere.

## Temeiul legal

::: ghid-temei
„Următoarele cheltuieli nu sunt deductibile: [...] dobânzile/majorările de întârziere, amenzile, confiscările și penalitățile, datorate către autoritățile române/străine, potrivit prevederilor legale, cu excepția celor aferente contractelor încheiate cu aceste autorități [...]"
— Legea 227/2015, art. 25 alin. (4) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă practic, atât contabil, cât și fiscal:

- **Contabil**, amenda se înregistrează ca o cheltuială de exploatare, în contul **6581 „Despăgubiri, amenzi și penalități"** (subgrupă a contului 658 „Alte cheltuieli de exploatare"), pe baza procesului-verbal de contravenție sau a deciziei ANAF care o stabilește.
- **Fiscal**, la calculul impozitului pe profit, valoarea din 6581 se adaugă înapoi la profitul impozabil, ca element nedeductibil — spre deosebire de cheltuielile cu deductibilitate limitată (protocol, cheltuieli sociale), amenzile nu au un plafon parțial deductibil, sunt nedeductibile în întregime.
- **Excepția din lege**: amenzile/penalitățile aferente unor contracte încheiate chiar cu autoritățile (nu sancțiuni administrative, ci clauze contractuale, de exemplu penalități de întârziere într-un contract de achiziție publică) rămân deductibile, pentru că nu au natura unei sancțiuni, ci a unei clauze contractuale asumate.
- Pentru microîntreprinderi, care nu au deduceri de cheltuieli (baza impozabilă fiind veniturile), distincția deductibil/nedeductibil nu se aplică în același fel — dar amenda rămâne, oricum, o cheltuială fără efect de reducere a bazei impozabile.

## Ce se greșește în practică

- Se scade amenda din profitul impozabil ca orice altă cheltuială, fără să se facă ajustarea de nedeductibilitate la calculul impozitului pe profit — eroare care duce direct la subdeclararea impozitului datorat.
- Se confundă amenda contravențională (nedeductibilă integral) cu o penalitate contractuală datorată unui partener comercial (nu unei autorități), care urmează regimul obișnuit al cheltuielilor, nu excepția de la art. 25 alin. (4) lit. b).
- Nu se distinge amenda propriu-zisă de eventualele dobânzi/majorări de întârziere asociate unei obligații fiscale neplătite la termen — ambele sunt nedeductibile, dar apar adesea pe documente separate.

## Ce face iConta.eu

Planul de conturi din iConta.eu (`core/plan_omfp.py`) include explicit contul **6581 „Despăgubiri, amenzi și penalități"**, folosit pentru înregistrarea acestui tip de cheltuieli. La data acestui ghid, aplicația **nu calculează automat, în cadrul declarației de impozit pe profit, ajustarea de nedeductibilitate** pentru sumele înregistrate în 6581 — evidențierea sumei ca element nedeductibil la calculul impozitului pe profit rămâne un pas pe care contabilul îl aplică manual, pe baza soldului contului.

[iConta.eu](/)
