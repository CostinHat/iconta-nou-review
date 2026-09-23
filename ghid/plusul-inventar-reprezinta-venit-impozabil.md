---
title: "Plusul de inventar reprezintă venit impozabil"
description: "De ce afirmația este adevărată doar parțial: plusul de stoc afectează imediat rezultatul, dar plusul de mijloc fix se reia treptat la venituri, pe măsura amortizării."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Plusul de inventar reprezintă venit impozabil

Afirmația din titlu e adevărată doar în parte — și diferența contează pentru calculul impozitului pe profit din anul constatării.

## Temeiul legal

::: ghid-temei
Contul 4754 "Plusuri de inventar de natura imobilizărilor" este încadrat în clasa 47 "Conturi
de subvenții, regularizare și asimilate" din planul de conturi (OMFP 1802/2014).
:::

Aceasta este distincția-cheie: un plus de **stoc** (371, 301, 302, 303, 345, 381) se compensează direct cu un cont de cheltuială sau venit (de exemplu 371=607) — deci reduce imediat o cheltuială de gestiune și, astfel, mărește rezultatul impozabil al anului în care se constată plusul.

Un plus de **mijloc fix** intră însă pe contul 4754, din clasa conturilor de subvenții/venituri în avans — nu pe un cont de venit direct. Fiind în această clasă, valoarea nu se consideră, de regulă, integral și imediat venit impozabil în anul constatării; mecanismul obișnuit pentru conturile din această clasă este reluarea treptată la venituri, pe măsura amortizării activului — analog modului în care funcționează o subvenție pentru investiții.

Nu am putut confirma, la nivelul modulului de inventariere propriu-zis, un mecanism explicit de reluare treptată a acestei valori la venituri — dacă acest calcul se face, el aparține unui alt modul (de amortizare sau de venituri în avans), nu logicii de inventariere în sine.

## Ce se greșește în practică

- Se tratează orice plus de inventariere — indiferent dacă e de stoc sau de mijloc fix — ca venit impozabil integral, în anul constatării.
- Se omite urmărirea reluării treptate la venituri a plusului de mijloc fix înregistrat pe 4754, pe măsura amortizării activului.

## Ce face iConta.eu

Modulul de inventariere din iConta.eu înregistrează corect distincția contabilă: plusul de stoc pe conturile de compensare directă (607, 601, 602, 603, 711, 608), plusul de mijloc fix pe contul 4754. Însă **nu calculează el însuși reluarea treptată la venituri a plusului de mijloc fix** — acest calcul, dacă e automatizat undeva în aplicație, ține de un alt modul (de amortizare), nu de ecranul de inventariere. Dacă lucrați cu un plus de mijloc fix semnificativ, verificați separat modul în care valoarea de pe 4754 ajunge, în timp, la rezultatul impozabil.

[iConta.eu](/)
