---
title: "Închiderea firmei și soldul TVA de recuperat"
description: "Ce se întâmplă cu un sold de TVA de recuperat la lichidarea unei firme, și de ce inspecția fiscală anticipată devine practic obligatorie atunci când firma e în procedură de lichidare voluntară sau insolvență."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Închiderea firmei și soldul TVA de recuperat

O firmă care intră în lichidare voluntară, cu un sold de TVA de recuperat rămas nesoluționat, nu mai beneficiază de rambursarea rapidă, cu inspecție fiscală ulterioară. Legea tratează explicit acest caz ca pe unul de risc și obligă la inspecție fiscală anticipată — adică înainte, nu după rambursare.

## Temeiul legal

::: ghid-temei
„(2) Prevederile alin. (1) nu se aplică deconturilor cu sume negative de TVA cu opțiune de rambursare, depuse de contribuabilii mari și mijlocii, [...] care se soluționează după efectuarea inspecției fiscale anticipate, în cazul în care: [...] c) pentru contribuabilul/plătitorul respectiv a fost declanșată procedura de lichidare voluntară sau a fost deschisă procedura de insolvență, cu excepția celor pentru care s-a confirmat un plan de reorganizare, în condițiile Legii nr. 85/2014 [...]."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 169 alin. (2) lit. c) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce înseamnă asta pentru soldul de TVA de recuperat la închiderea firmei:

- Regula generală (rambursare rapidă, cu inspecție **ulterioară**) **nu se aplică** deconturilor negative de TVA cu opțiune de rambursare, dacă firma a intrat deja în lichidare voluntară sau insolvență — ANAF va face inspecție fiscală **anticipată** (înainte de a rambursa suma).
- Aceeași regulă se aplică și contribuabililor mici, pentru care alin. (3) prevede un criteriu similar — practic, orice firmă în lichidare care solicită rambursare de TVA se supune inspecției fiscale anticipate, indiferent de mărime.
- Excepția o constituie firmele aflate în insolvență **cu plan de reorganizare confirmat** printr-o sentință judecătorească — acestea rămân sub regimul obișnuit de rambursare cu inspecție ulterioară.

## Ce se greșește în practică

- Se depune declarația de radiere a firmei fără să se fi soluționat în prealabil soldul de TVA de recuperat, prelungind astfel procesul de lichidare până la finalizarea inspecției fiscale.
- Se așteaptă o rambursare rapidă de TVA după deschiderea procedurii de lichidare voluntară, ignorând faptul că legea impune, în acest caz, inspecție fiscală anticipată, cu termene mai lungi.
- Se confundă lichidarea voluntară (dizolvare urmată de lichidare, potrivit Legii 31/1990) cu insolvența cu plan de reorganizare confirmat — doar aceasta din urmă rămâne exceptată de la inspecția anticipată.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are o funcționalitate dedicată procedurii de lichidare** și nu semnalează automat că un sold de TVA de recuperat va intra sub regimul inspecției fiscale anticipate atunci când firma își schimbă statutul în lichidare. Aplicația calculează și urmărește soldul TVA de recuperat din deconturile D300 generate (`core/d300.py`), dar decizia și procedura de soluționare a acestui sold la închiderea firmei rămân în sarcina contabilului, în colaborare cu organul fiscal.

[iConta.eu](/)
