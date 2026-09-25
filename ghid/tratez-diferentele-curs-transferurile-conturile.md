---
title: "Cum tratez diferențele de curs la transferurile între conturile firmei"
description: "Când un transfer între conturile bancare ale aceleiași firme generează diferențe de curs valutar recunoscute contabil și când nu."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum tratez diferențele de curs la transferurile între conturile firmei

Firmele cu mai multe conturi bancare — în lei și în valută, la bănci diferite — mută frecvent bani între ele. Întrebarea contabilă e dacă aceste mișcări interne generează diferențe de curs valutar de recunoscut în rezultat, sau sunt „neutre" fiscal.

## Temeiul legal

::: ghid-temei
„317. (1) În înțelesul prezentelor reglementări, o tranzacție în valută este o tranzacție care este exprimată sau necesită decontarea într-o altă monedă decât moneda națională (leu) [...] c) achiziționează sau cedează într-o altă manieră active, contractează sau achită datorii exprimate în valută. [...] (3) Diferența de curs valutar este diferența ce rezultă din conversia unui anumit număr de unități ale unei monede într-o altă monedă la cursuri de schimb diferite.
325. (1) La finele fiecărei luni, creanțele și datoriile în valută se evaluează la cursul de schimb al pieței valutare, comunicat de Banca Națională a României din ultima zi bancară a lunii în cauză. Diferențele de curs înregistrate se recunosc în contabilitate la venituri sau cheltuieli din diferențe de curs valutar, după caz. (2) [...] b) cursul de schimb al pieței valutare comunicat de Banca Națională a României, din ultima zi bancară a lunii în cauză, pentru evaluarea creanțelor și datoriilor în valută, a disponibilităților în valută și a altor valori de trezorerie [...] existente în sold la sfârșitul lunii."
— OMFP nr. 1802/2014, pct. 317 alin. (1) lit. c) și alin. (3), pct. 325 alin. (1)-(2) lit. b) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Din text rezultă distincția care contează în practică:

- **Un transfer între două conturi ale firmei, în aceeași monedă** (de exemplu dintr-un cont EUR la altă bancă, tot în EUR) nu e, prin el însuși, o „tranzacție în valută" în sensul art. 317 alin. (1) — nu implică o conversie dintr-o monedă în alta, deci nu generează o diferență de curs la momentul transferului.
- **Disponibilitățile în valută rămân însă supuse evaluării lunare** la cursul BNR din ultima zi bancară a lunii (pct. 325). Dacă transferul are loc într-o lună, iar soldul respectiv trece prin evaluarea de sfârșit de lună înainte sau după mutare, diferența de curs apare oricum — nu din transfer, ci din evaluarea periodică obligatorie a soldului în valută.
- **Un transfer care implică schimb valutar** (de exemplu conversia unei sume din EUR în RON pentru a fi mutată în alt cont) este, prin definiție, o tranzacție în valută — diferența dintre cursul folosit la conversie și cursul la care suma era înregistrată anterior se recunoaște ca venit sau cheltuială din diferențe de curs.

## Ce se greșește în practică

- Se înregistrează o diferență de curs „din transfer" la fiecare mutare de bani între conturi în aceeași monedă, deși simpla mutare între conturi proprii, fără schimb valutar, nu generează diferență — ce generează diferență e evaluarea periodică a soldului, nu mișcarea în sine.
- Se omite evaluarea lunară a disponibilităților în valută rămase în cont la sfârșitul lunii, considerându-se, greșit, că doar tranzacțiile efective (încasări/plăți către terți) trebuie evaluate la curs.
- Se tratează conversia efectivă dintr-o monedă în alta (schimb valutar la mutarea banilor) ca pe o simplă mișcare de trezorerie, fără să se recunoască diferența de curs rezultată din conversie.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are un modul dedicat evaluării automate lunare a diferențelor de curs valutar pentru disponibilitățile bancare** — nu am găsit în cod o funcție care să recalculeze automat, la finalul fiecărei luni, soldurile în valută la cursul BNR și să genereze diferențele favorabile/nefavorabile aferente. Înregistrarea corectă a transferurilor între conturile firmei (cu sau fără conversie valutară) și evaluarea periodică a soldurilor în valută rămân, la acest moment, operațiuni introduse manual de contabil.

[iConta.eu](/)
