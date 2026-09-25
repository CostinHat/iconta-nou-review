---
title: "Regimul fiscal al divizării firmei la impozitul pe profit"
description: "Neutralitatea fiscală a operațiunilor de fuziune și divizare la impozitul pe profit, conform Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Regimul fiscal al divizării firmei la impozitul pe profit

Divizarea unei societăți — totală sau parțială — nu generează, prin ea însăși, un impozit pe profit de plată. Codul fiscal instituie explicit un regim de neutralitate fiscală pentru aceste operațiuni, cu condiții precise.

## Temeiul legal

::: ghid-temei
„Articolul 32 Regimul fiscal care se aplică fuziunilor, divizărilor totale, divizărilor parțiale, transferurilor de active și achizițiilor de titluri de participare între persoane juridice române
(1) Prevederile prezentului articol se aplică următoarelor operațiuni de fuziune, divizare totală, divizare parțială, transferurilor de active și operațiunilor de achiziție de titluri de participare, efectuate între persoane juridice române potrivit legii [...].
Operațiunile de fuziune, divizare sub orice formă nu sunt transferuri impozabile pentru diferența dintre prețul de piață al elementelor din activ și pasiv transferate și valoarea lor fiscală."
— Legea 227/2015 (Codul fiscal), art. 32 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Principiile de bază ale acestui regim de neutralitate, aplicabil divizărilor între persoane juridice române:

- **Nu se generează impozit pe profit** la momentul divizării pentru diferența dintre valoarea de piață și valoarea fiscală a activelor și pasivelor transferate — societatea beneficiară preia elementele la valoarea lor fiscală, nu la cea de piață.
- Condiția pentru păstrarea neutralității: **societatea beneficiară trebuie să calculeze amortizarea și orice câștig sau pierdere aferente activelor transferate în aceleași condiții în care le-ar fi calculat societatea cedentă** dacă divizarea nu ar fi avut loc — adică se continuă tratamentul fiscal anterior, nu se „resetează" valorile.
- **Pierderea fiscală** a societății care își încetează existența ca efect al unei divizări totale se recuperează de societățile beneficiare, **proporțional cu activele transferate**, potrivit proiectului de divizare.
- Regimul de neutralitate **nu se aplică** dacă operațiunea are drept consecință frauda sau evaziunea fiscală, constatată în condițiile legii.
- Distinct de impozitul pe profit, emiterea de titluri de participare către asociați în legătură cu divizarea nu reprezintă, la rândul ei, un transfer impozabil pentru aceștia, cu respectarea condițiilor din același articol.

## Ce se greșește în practică

- Se calculează impozit pe profit pe diferența dintre valoarea de piață și valoarea contabilă a activelor transferate, ignorând regimul de neutralitate fiscală prevăzut explicit de art. 32.
- Se împarte pierderea fiscală nerecuperată arbitrar între societățile beneficiare, în loc de proporțional cu activele efectiv transferate, conform proiectului de divizare.
- Se presupune că neutralitatea fiscală se aplică automat oricărei reorganizări, fără să se verifice că operațiunea nu urmărește, de fapt, frauda sau evaziunea fiscală — situație în care regimul special nu se mai aplică.

## Ce face iConta.eu

Am verificat în `core/lichidare.py` și modulele fiscale conexe (`core/d101.py`): aplicația **nu are un flux dedicat operațiunilor de divizare** — nu am găsit o funcție care să aplice automat regimul de neutralitate fiscală de la art. 32 (transfer de valori fiscale, alocare proporțională a pierderii fiscale între societățile beneficiare). O astfel de reorganizare se tratează, la acest moment, în afara aplicației, cu asistență de specialitate.

[iConta.eu](/)
