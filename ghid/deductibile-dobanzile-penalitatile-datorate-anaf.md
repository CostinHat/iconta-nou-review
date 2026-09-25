---
title: "Sunt deductibile dobânzile și penalitățile datorate ANAF?"
description: "De ce majorările de întârziere, amenzile și penalitățile datorate statului sunt cheltuieli nedeductibile la calculul impozitului pe profit, conform Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Sunt deductibile dobânzile și penalitățile datorate ANAF?

Nu. Indiferent cât de mari sunt sumele plătite ca dobânzi/majorări de întârziere sau ca penalități către ANAF, ele nu reduc baza impozabilă a impozitului pe profit. Legea le exclude expres din categoria cheltuielilor deductibile.

## Temeiul legal

::: ghid-temei
„(4) Următoarele cheltuieli nu sunt deductibile: [...] b) dobânzile/majorările de întârziere, amenzile, confiscările și penalitățile, datorate către autoritățile române/străine, potrivit prevederilor legale, cu excepția celor aferente contractelor încheiate cu aceste autorități;"
— Legea nr. 227/2015 (Codul fiscal), art. 25 alin. (4) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Câteva precizări importante din chiar textul citat:

- Nedeductibilitatea vizează sumele **datorate către autorități** — române sau străine — ca urmare a nerespectării unor obligații legale (întârziere la plată, contravenții, confiscări), nu orice fel de dobândă sau penalitate.
- Există o **excepție explicită**: dobânzile, majorările sau penalitățile aferente unor contracte încheiate cu acele autorități rămân deductibile — de exemplu penalitățile de întârziere dintr-un contract comercial în care statul e parte, distincte de sancțiunile aplicate din oficiu pentru nerespectarea legii.
- Regula se aplică indiferent de mărimea sumei sau de motivul întârzierii — chiar și o majorare mică, plătită pentru câteva zile de întârziere la o declarație sau la o plată, rămâne nedeductibilă.
- Penalitățile/dobânzile plătite unor parteneri comerciali privați (nu autorități) pentru întârzieri contractuale nu intră sub incidența acestei excluderi — ele urmează regimul general de deductibilitate al cheltuielilor.

## Ce se greșește în practică

- Se include în calculul cheltuielilor deductibile suma totală a dobânzilor/majorărilor plătite ANAF, fără a le scoate din rezultatul fiscal la calculul impozitului pe profit.
- Se confundă penalitățile contractuale plătite unui partener comercial (deductibile, ca regulă) cu penalitățile datorate autorităților (nedeductibile), tratându-le identic.
- Se presupune, greșit, că penalitățile devin deductibile dacă suma e mică sau dacă întârzierea nu a fost „din vina firmei".

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează rezultatul fiscal și impozitul pe profit prin `core/d101.py`, care aplică regulile de deductibilitate ale Codului fiscal pe baza contului contabil pe care e înregistrată fiecare cheltuială. Dacă dobânzile/penalitățile ANAF sunt contate corect, în conturile dedicate cheltuielilor cu penalitățile fiscale, aplicația le tratează ca nedeductibile la calculul impozitului. Aplicația **nu verifică însă natura fiecărei sume** înregistrate manual de utilizator — dacă o penalitate ANAF e introdusă greșit pe un cont de cheltuială deductibilă, iConta.eu nu semnalează automat eroarea; clasificarea corectă a fiecărei sume rămâne responsabilitatea contabilului.

[iConta.eu](/)
