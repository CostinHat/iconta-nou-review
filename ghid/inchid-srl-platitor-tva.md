---
title: Cum închid un SRL plătitor de TVA?
description: Ce presupune, la nivel de TVA, lichidarea unei societăți plătitoare — de la vânzarea activelor rămase până la depunerea manuală a declarației de radiere din vector fiscal.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum închid un SRL plătitor de TVA?

Statutul de plătitor de TVA nu se „oprește" automat la decizia de dizolvare — societatea rămâne plătitoare de TVA pe toată durata operațiunilor de lichidare (vânzări de active, încasări de creanțe) și abia radierea din registrul comerțului pune capăt și calității de plătitor.

## Temeiul legal

::: ghid-temei
„Societatea își păstrează personalitatea juridică pentru operațiunile lichidării, până la terminarea acesteia."
— L31/1990, art. 233 alin. (4)
:::

Cât timp societatea există juridic și desfășoară operațiuni economice (vânzarea unui activ, de exemplu), regimul de TVA aplicabil acestor operațiuni rămâne cel obișnuit al unui plătitor.

## Ce se greșește în practică

Se omite frecvent completarea cotei de TVA la vânzarea unui activ în cursul lichidării, considerând-o „subînțeleasă". Funcția de calcul din motorul de lichidare al iConta.eu (`core/lichidare.py`, `nota_vanzare_activ`) nu are nicio cotă de TVA implicită — cota trebuie introdusă explicit la fiecare operațiune, tocmai pentru ca nota contabilă generată să nu rămână „înghețată" pe o cotă veche dacă legea se schimbă.

O a doua greșeală este să se creadă că iConta.eu poate genera și depune declarația de mențiuni vector fiscal (D700) necesară, de regulă, la scoaterea societății din evidența plătitorilor de TVA odată cu radierea.

## Ce face iConta.eu

La vânzarea unui activ rămas în patrimoniu, ecranul „Lichidare / radiere firmă" (operația „Vânzare activ la lichidare") generează nota contabilă cu TVA colectată inclusă: `461 = 7583 + 4427`, pe baza cotei de TVA introduse explicit de utilizator.

Pentru scoaterea efectivă din vectorul fiscal (anularea codului de TVA), aplicația **nu generează** declarația D700. Conform dosarului de cercetare pentru F057, această declarație este marcată explicit ca respinsă la nivel de funcționalitate:

::: ghid-temei
„Declarația D700 (mențiuni vector fiscal) - RESPINS", stare „RESPINS 20.07.2026"
— FUNCTIONALITATI.csv, rândul F196
:::

Motivul tehnic confirmat în dosar: D700 este un formular de tip SmartPDF, nu un XML validabil precum alte declarații (D230, D311), iar validatorul disponibil întoarce eroare pe orice încercare de validare standalone; lipsește totodată și actul OPANAF cu instrucțiunile câmp-cu-câmp necesare unei implementări corecte. Concluzia practică: **D700 se depune manual, în afara aplicației**, de către contabil, la scoaterea societății din evidența plătitorilor de TVA.

[iConta.eu](/)
