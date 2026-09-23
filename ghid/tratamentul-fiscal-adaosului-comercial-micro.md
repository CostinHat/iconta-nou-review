---
title: "Tratamentul fiscal al adaosului comercial la micro"
description: "Ce documentează concret metoda global-valorică pentru adaosul comercial — și de ce acest ghid nu poate confirma o particularizare fiscală pentru microîntreprinderi."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Tratamentul fiscal al adaosului comercial la micro

Acest ghid pornește de la un titlu care cere un răspuns punctual: dacă regimul de impozitare pe veniturile microîntreprinderilor schimbă cu ceva modul de calcul și înregistrare a adaosului comercial la comercianții cu amănuntul. Spunem onest, de la început: dosarul tehnic pe care se bazează acest ghid documentează exclusiv mecanismul contabil (OMFP 1802/2014) și **nu conține niciun text legal privind impozitul pe veniturile microîntreprinderilor**. Tot ce urmează se limitează la partea confirmată — mecanismul contabil al adaosului.

## Temeiul legal

::: ghid-temei
OMFP 1802/2014, Anexa 1 — Reglementări contabile, pct. 286 alin. (1): „... pentru determinarea costului pot fi folosite, de asemenea, metoda costului standard, în activitatea de producție sau metoda prețului cu amănuntul, în comerțul cu amănuntul."

(Text consolidat OMFP 1802/2014, verificat pe mirrorul local la 17.09.2026.)
:::

Metoda prețului cu amănuntul (global-valorică) este o regulă de **evidență contabilă a stocurilor**, reglementată de OMFP 1802/2014, pct. 286. Ea stabilește cum se separă, din prețul de vânzare, costul de achiziție (607), adaosul comercial (378) și TVA neexigibilă (4428) — indiferent de forma de impozitare a firmei (impozit pe profit sau impozit pe veniturile microîntreprinderilor).

## Ce se greșește în practică

O confuzie frecventă este amestecarea a două lucruri distincte: (1) modul în care se **contabilizează** adaosul comercial (reglementat de OMFP 1802/2014, pct. 286, verificat mai sus) și (2) modul în care se **impozitează** cifra de afaceri sau profitul firmei (reglementat de Codul fiscal, la titlul dedicat microîntreprinderilor). Dosarul tehnic pe care se bazează acest ghid a verificat doar mecanismul contabil — nu a găsit și nu cităm niciun temei legal pentru partea a doua, ca să nu inventăm o regulă.

## Ce face iConta.eu

Motorul de calcul al gestiunii global-valorice (`core/stocuri.py`, `core/stocuri_api.py`) aplică formula coeficientului de repartizare (K) și generează automat, ca ciornă, nota lunară de descărcare (607/378/4428), validată manual de contabil — mecanism descris pe larg în ghidul „Calculul adaosului comercial la ieșirea din gestiune". Conform cercetării care stă la baza acestui ghid, acest mecanism **nu diferă în funcție de regimul de impozitare** al firmei (nu există în cod nicio ramură separată „microîntreprindere" pentru F088). Pentru tratamentul fiscal propriu-zis al veniturilor microîntreprinderii, recomandăm consultarea unui ghid dedicat acelui subiect, bazat pe un dosar de cercetare privind Codul fiscal — nu pe acest dosar, care acoperă doar evidența stocurilor.

[iConta.eu](/)
