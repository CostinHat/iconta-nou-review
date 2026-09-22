---
title: Ce obligații TVA are o firmă IT neplătitoare care facturează în UE?
description: D301 declară exclusiv achiziții intracomunitare, nu vânzări — o firmă IT neplătitoare care facturează servicii către clienți din UE nu depune D301 pentru aceste facturi, chiar dacă trebuie să se înregistreze conform art. 317.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce obligații TVA are o firmă IT neplătitoare care facturează în UE?

O firmă IT română neplătitoare de TVA care emite facturi de servicii (dezvoltare software, consultanță, mentenanță) către clienți persoane impozabile din alte state membre UE se află într-o situație diferită de cea a unei firme care *cumpără* servicii din UE. Este important de clarificat de la început: acest scenariu **nu implică depunerea decontului special D301**.

## Temeiul legal

::: ghid-temei
**Articolul 324 — Decontul special de taxă și alte declarații**
(1) Decontul special de taxă se depune la organele fiscale competente de către persoanele care nu sunt înregistrate și care nu trebuie să se înregistreze conform art. 316, astfel:
a) pentru achiziții intracomunitare de bunuri taxabile, altele decât cele prevăzute la lit. b) și c), de către persoanele impozabile înregistrate conform art. 317;
b) pentru achiziții intracomunitare de mijloace de transport noi, de către orice persoană, indiferent dacă este sau nu înregistrată conform art. 317;
c) pentru achiziții intracomunitare de produse accizabile, de către persoanele impozabile și persoanele juridice neimpozabile, indiferent dacă sunt sau nu înregistrate conform art. 317;
d) pentru operațiunile și de către persoanele obligate la plata taxei, conform art. 307 alin. (2)-(4) și (6);
e) pentru operațiunile și de către persoanele obligate la plata taxei conform art. 307 alin. (5), cu excepția situației în care are loc un import de bunuri sau o achiziție intracomunitară de bunuri.

**Articolul 278 alin. (2)**: Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. [...]

**Alin. (10)**: Înregistrarea în scopuri de TVA conform prezentului articol nu conferă persoanei calitatea de persoană înregistrată normal în scopuri de TVA, acest cod fiind utilizat numai pentru operațiunile prevăzute la alin. (1)-(2^1).
:::

## De ce D301 nu se aplică vânzărilor către clienți din UE

Așa cum se vede în textul art. 324 alin. (1), toate cele cinci litere care descriu operațiunile pentru care se depune D301 privesc exclusiv **achiziții** — de bunuri, mijloace de transport noi, produse accizabile sau operațiuni pentru care beneficiarul (nu furnizorul) este obligat la plata taxei. Nicio literă nu vizează situația în care firma română este cea care **emite** factura către un client din UE.

Regula de la art. 278 alin. (2) funcționează simetric: la fel cum o firmă română care primește un serviciu de la un furnizor UE datorează TVA în România (pentru că ea este beneficiarul), o firmă română care vinde un serviciu unui client persoană impozabilă din alt stat UE nu datorează TVA în România pentru acea prestare — locul prestării este considerat a fi în statul clientului, unde acesta, ca beneficiar, poate avea la rândul lui obligația de taxare inversă.

Această situație implică totuși o obligație de înregistrare: conform dosarului de temei legal, firma trebuie să solicite înregistrarea specială conform art. 317 (alin. (1) lit. b), simetric literei c) care privește achizițiile) înainte de a presta astfel de servicii către clienți din UE. Această înregistrare specială nu transformă firma într-un plătitor de TVA "normal" (art. 317 alin. (10)) și nu generează, prin ea însăși, obligația de a depune D301 — D301 rămâne o declarație despre achiziții, iar facturile emise de firma IT către clienții UE nu apar deloc în acest formular.

## Ce se greșește în practică

- Se încearcă declararea facturilor emise către clienți UE în D301, prin analogie cu achizițiile de servicii — D301 nu are nicio secțiune pentru operațiuni de ieșire (vânzări).
- Se ignoră obligația de înregistrare conform art. 317 înainte de prima prestare de servicii către un client UE, considerând că înregistrarea e necesară doar la achiziții.
- Se presupune că înregistrarea specială art. 317 transformă firma într-un plătitor de TVA "normal", deși legea exclude explicit acest efect.
- Se confundă obligațiile de raportare aferente vânzărilor intracomunitare de servicii cu cele aferente achizițiilor — sunt declarații și fluxuri fiscale diferite.

## Ce face iConta.eu

Motorul D301 din iConta.eu (`core/d301.py`, `core/d301_operatiuni_api.py`) tratează exclusiv achiziții intracomunitare — nu există niciun cod în acest motor pentru operațiuni de ieșire (facturare către clienți din UE). Pentru o firmă IT neplătitoare care facturează servicii către clienți din UE, D301 nu este declarația relevantă și nu trebuie completată pentru aceste facturi de vânzare; obligațiile fiscale legate de aceste vânzări (inclusiv înregistrarea specială art. 317) se gestionează prin alte fluxuri decât cel de introducere a operațiunilor D301.

[iConta.eu](/)
