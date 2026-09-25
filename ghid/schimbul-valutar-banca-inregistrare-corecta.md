---
title: "Schimbul valutar la bancă: înregistrare corectă"
description: "Cum se înregistrează în contabilitate o operațiune de schimb valutar la bancă și diferența de curs care rezultă față de cursul BNR folosit deja în evidență."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Schimbul valutar la bancă: înregistrare corectă

Când firma schimbă valută la bancă (vinde EUR/USD încasat de la un client extern, sau cumpără valută pentru a plăti un furnizor), banca aplică propriul ei curs comercial, care aproape niciodată nu coincide cu cursul BNR la care disponibilul în valută era deja evidențiat în contabilitate. Diferența dintre cele două cursuri nu se pierde — se înregistrează separat, ca venit sau cheltuială din diferențe de curs valutar.

## Temeiul legal

::: ghid-temei
„317. - [...] (2) Cursul de schimb valutar este raportul de schimb dintre două monede. (3) Diferența de curs valutar este diferența ce rezultă din conversia unui anumit număr de unități ale unei monede într-o altă monedă la cursuri de schimb diferite.
319. - O tranzacție în valută trebuie înregistrată inițial la cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunii.
322. - (1) Diferențele de curs valutar care apar cu ocazia decontării creanțelor și datoriilor în valută la cursuri diferite față de cele la care au fost înregistrate inițial pe parcursul lunii sau față de cele la care sunt înregistrate în contabilitate trebuie recunoscute în luna în care apar, ca venituri sau cheltuieli din diferențe de curs valutar.
325. - (1) La finele fiecărei luni, creanțele și datoriile în valută se evaluează la cursul de schimb al pieței valutare, comunicat de Banca Națională a României din ultima zi bancară a lunii în cauză. [...] b) cursul de schimb al pieței valutare comunicat de Banca Națională a României, din ultima zi bancară a lunii în cauză, pentru evaluarea creanțelor și datoriilor în valută, a disponibilităților în valută și a altor valori de trezorerie [...] existente în sold la sfârșitul lunii."
— OMFP 1802/2014 (reglementările contabile), pct. 317, 319, 322, 325 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Mecanismul complet al operațiunii, din normă:

- **Evidența valutei se ține la cursul BNR**, comunicat la data operațiunii (pct. 319) — nu la cursul comercial al băncii. Contul de disponibil în valută (5124) crește/scade cu suma efectivă în valută, convertită la cursul BNR al zilei.
- **Schimbul propriu-zis la bancă** e o decontare a disponibilului în valută: se scoate suma din 5124 (la cursul BNR la care era evidențiată) și intră suma în lei rezultată efectiv din banca (5121), la cursul comercial aplicat de bancă pentru acea tranzacție.
- **Diferența** dintre cei doi lei — cel calculat la cursul BNR al zilei și cel obținut efectiv de la bancă — e o diferență de curs valutar (pct. 317 alin. 3) și se recunoaște integral în luna în care are loc schimbul (pct. 322 alin. 1), ca venit (765) dacă e favorabilă sau cheltuială (665) dacă e nefavorabilă.
- La finalul fiecărei luni, orice sold rămas în valută (disponibil, creanțe, datorii) se **reevaluează** la cursul BNR din ultima zi bancară a lunii (pct. 325), indiferent dacă a avut loc vreun schimb — deci diferențele de curs apar și fără nicio tranzacție efectivă la bancă.

## Ce se greșește în practică

- Se înregistrează suma primită de la bancă direct în 5121, fără să se scoată mai întâi din 5124 la cursul BNR la care era evidențiată — astfel diferența de curs dispare din contabilitate în loc să fie recunoscută separat pe 665/765.
- Se confundă cursul comercial al băncii (folosit doar pentru calculul sumei efective în lei primite/plătite) cu cursul BNR (folosit pentru evidența contabilă a soldului în valută) — cele două cursuri au roluri diferite și aproape niciodată aceeași valoare.
- Se omite reevaluarea lunară a soldurilor rămase în valută, considerând că diferențele de curs apar doar când se face efectiv un schimb la bancă.

## Ce face iConta.eu

Motorul de diferențe de curs valutar (`core/diferente_curs.py`) calculează, pur, diferența 665/765 rezultată la decontarea unei creanțe, datorii sau a unui disponibil în valută (inclusiv, deci, la un schimb valutar la bancă) — pe baza cursului inițial și a cursului final introduse, cu regula de semn corectă (câștig 765 dacă valoarea crește pentru o creanță/disponibil, pierdere 665 dacă e o datorie). Curs BNR pentru facturi e preluat automat prin modulul dedicat (curs BNR pentru facturare/TVA), dar pentru o operațiune de schimb valutar la bancă propriu-zisă, cursul comercial obținut efectiv de la bancă și data operațiunii se introduc de contabil — aplicația nu descarcă automat cotațiile băncilor comerciale.

[iConta.eu](/)
