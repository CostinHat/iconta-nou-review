---
title: "Ce diferență este între dobândă și penalitate de întârziere?"
description: "Diferența dintre dobânda și penalitatea de întârziere aplicate de ANAF pentru obligații fiscale neplătite la termen, cu ratele valabile."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce diferență este între dobândă și penalitate de întârziere?

Când o obligație fiscală nu e plătită la scadență, ANAF nu calculează un singur tip de accesoriu, ci două, în paralel: dobânda (compensează statul pentru banii neîncasați la timp) și penalitatea de întârziere (sancționează întârzierea). Se aplică amândouă, cumulat, nu alternativ.

## Temeiul legal

::: ghid-temei
„Pentru neachitarea la termenul de scadență de către debitor a obligațiilor fiscale principale, se datorează după acest termen dobânzi și penalități de întârziere. [...] Nivelul dobânzii este de 0,02% pentru fiecare zi de întârziere. [...] Nivelul penalității de întârziere este de 0,01% pentru fiecare zi de întârziere."
— Legea 207/2015 (Codul de procedură fiscală), art. 173 alin. (1), art. 174 alin. (5) și art. 176 alin. (2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Diferențele esențiale între cele două:

- **Dobânda** (0,02%/zi) se calculează pe toată perioada de întârziere, fără excepție, pentru orice obligație fiscală principală neplătită la termen.
- **Penalitatea de întârziere** (0,01%/zi) se calculează separat, cumulându-se cu dobânda — cele două nu se exclud reciproc.
- Nu se datorează dobânzi și penalități de întârziere pentru amenzi, alte obligații fiscale accesorii, cheltuieli de executare silită sau cheltuieli judiciare (art. 173 alin. 2) — accesoriile se aplică doar la obligațiile principale.
- Este distinctă de **penalitatea de nedeclarare** (0,08%/zi), care se aplică doar când obligația a fost nedeclarată sau declarată incorect și stabilită ulterior de organul fiscal prin decizie de impunere (art. 181).

## Ce se greșește în practică

- Se confundă penalitatea de întârziere (0,01%/zi, pentru plata cu întârziere a unei sume corect declarate) cu penalitatea de nedeclarare (0,08%/zi, pentru sume nedeclarate deloc sau greșit) — sunt regimuri diferite, cu rate diferite.
- Se calculează doar dobânda, omițând penalitatea de întârziere, sau invers — legal se datorează amândouă simultan.
- Se presupune că suma accesoriilor se oprește la data la care contribuabilul „știe" de datorie — de fapt curge de la scadență până la stingerea efectivă a sumei.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu are un modul dedicat de calcul automat al dobânzilor și penalităților de întârziere pentru obligații fiscale restante — aplicația oferă evidența contabilă generală (facturi, state de plată, declarații) și un motor de urmărire a scadențelor declarative (`core/control_fiscal_api.py`), dar simularea accesoriilor pentru sume neplătite la termen rămâne un calcul pe care contabilul îl face separat, de regulă pe baza fișei pe plătitor eliberate de ANAF (care conține valorile finale oficiale).

[iConta.eu](/)
