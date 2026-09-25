---
title: "Cum se calculează plafonul pentru vânzările la distanță în UE?"
description: "Pragul unic de 10.000 euro pentru vânzările intracomunitare de bunuri la distanță și pentru serviciile B2C transfrontaliere, cu temeiul din Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se calculează plafonul pentru vânzările la distanță în UE?

O firmă românească care vinde online către clienți persoane fizice din alte state membre trebuie să știe un singur prag: cât timp rămâne sub el, aplică TVA românesc; odată depășit, trece pe TVA-ul țării de destinație (de regulă prin OSS). Pragul e unic, la nivelul întregii Uniuni, nu separat pe fiecare țară.

## Temeiul legal

::: ghid-temei
„c) valoarea totală, fără TVA, a operațiunilor prevăzute la lit. b) nu depășește, în anul calendaristic curent, 10.000 euro sau echivalentul acestei sume în moneda națională și nici nu a depășit această sumă în cursul anului calendaristic precedent. (2) Atunci când, în cursul unui an calendaristic, pragul prevăzut la alin. (1) lit. c) este depășit, prevederile art. 275 alin. (2) și art. 278 alin. (5) lit. h) se aplică de la momentul depășirii pragului."
— Legea nr. 227/2015 (Codul fiscal), art. 278^1 alin. (1) lit. c) și alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce trebuie reținut din calcul:

- Plafonul de **10.000 euro** e **unic, cumulat** pentru toate vânzările la distanță de bunuri și toate serviciile de telecomunicații/radiodifuziune/electronice prestate către persoane neimpozabile din **toate** celelalte state membre — nu se calculează separat, câte 10.000 euro pentru fiecare țară de destinație.
- Echivalentul în lei al pragului e fixat, prin lege, la **46.337 lei**, calculat cu cursul BCE de la data adoptării directivei europene relevante — nu se recalculează anual în funcție de cursul curent.
- Testul se face pe **doi ani**: pragul se verifică atât pentru anul calendaristic curent, cât și pentru precedentul — dacă a fost depășit anul trecut, firma nu se mai poate încadra sub prag anul acesta, indiferent de cifrele curente.
- Odată depășit pragul, regimul se schimbă **de la momentul depășirii**, nu de la începutul anului sau de la o dată viitoare — locul livrării devine statul membru de destinație, iar TVA se declară acolo, de regulă prin regimul special OSS (One Stop Shop).
- Firmele stabilite în România pot **opta** pentru aplicarea regimului „la destinație" chiar și sub prag, dar opțiunea, o dată făcută, se aplică pentru minimum doi ani calendaristici.

## Ce se greșește în practică

- Se calculează plafonul separat, pe fiecare țară de destinație, presupunând că fiecare are propriul prag de 10.000 euro — pragul e unic, la nivel de Uniune, pentru toate destinațiile cumulate.
- Se ignoră testul pe anul precedent, aplicând pragul doar la vânzările din anul curent — o firmă care l-a depășit anul trecut nu mai beneficiază de scutire anul acesta, chiar dacă vânzările curente sunt mici.
- Se continuă facturarea cu TVA românesc după depășirea pragului în cursul anului, așteptând începutul anului următor pentru schimbarea regimului — legea cere schimbarea imediată, de la momentul depășirii.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu calculează automat plafonul cumulat de 10.000 euro pentru vânzările la distanță și nu semnalează depășirea lui — urmărirea acestui prag și schimbarea regimului de TVA la momentul depășirii rămân în sarcina contabilului. Aplicația are un modul pentru declarația D398 (`core/d398.py`), prin care se poate genera declarația specială de TVA pentru regimurile speciale OSS (UE, non-UE, import/IOSS) odată ce firma s-a înregistrat în regim — dar declarația e completată manual, pe baza valorilor introduse de contabil pe fiecare stat membru de consum, nu preluate automat din facturile emise.

[iConta.eu](/)
