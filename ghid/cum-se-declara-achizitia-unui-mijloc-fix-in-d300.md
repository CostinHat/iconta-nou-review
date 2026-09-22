---
title: Cum se declară achiziția unui mijloc fix în D300?
description: Regula de bază e simplă — dreptul de deducere ia naștere la exigibilitate — dar dacă mijlocul fix e un vehicul rutier motorizat neutilizat exclusiv economic, deducerea se limitează la 50%, iar aplicația nu aplică automat această limitare.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se declară achiziția unui mijloc fix în D300?

Un mijloc fix se declară în D300 ca orice altă achiziție deductibilă, pe cota corespunzătoare. Diferența apare la vehiculele rutiere motorizate, unde legea limitează deducerea la 50% dacă nu sunt folosite exclusiv în scop economic — o regulă pe care aplicația nu o aplică automat.

## Temeiul legal

::: ghid-temei
„(1) Dreptul de deducere ia naștere la momentul exigibilității taxei.”
— art.297 alin.(1) Cod fiscal

„(1) Prin excepție de la prevederile art. 297 se limitează la 50% dreptul de deducere a taxei
aferente cumpărării, achiziției intracomunitare, importului, închirierii sau leasingului de
vehicule rutiere motorizate și a taxei aferente cheltuielilor legate de vehiculele aflate în
proprietatea sau în folosința persoanei impozabile, în cazul în care vehiculele nu sunt
utilizate exclusiv în scopul activității economice.
(2) Restricția prevăzută la alin. (1) nu se aplică vehiculelor rutiere motorizate având o
masă totală maximă autorizată care depășește 3.500 kg sau mai mult de 9 scaune [...]”
— art.298 alin.(1)-(2) Cod fiscal

„Rândul 24 - se înscriu informaţiile din jurnalul de cumpărări privind baza de impozitare şi
taxa pe valoarea adăugată deductibilă aferentă achiziţiilor din ţară de bunuri şi servicii,
taxabile cu cota de 21%, altele decât cele înscrise la rândul 27 [...]”
— OPANAF 174/2026, instrucțiuni rd.24
:::

## Regula generală și excepția vehiculelor

Pentru majoritatea mijloacelor fixe (utilaje, echipamente, mobilier, clădiri), dreptul de deducere ia naștere la momentul exigibilității TVA și se declară integral la rândul de achiziții pe cota corespunzătoare (de regulă rd.24 pentru 21%), din jurnalul de cumpărări.

Excepția privește strict vehiculele rutiere motorizate: dacă vehiculul nu e utilizat exclusiv în scop economic, dreptul de deducere se limitează la 50% din TVA aferentă cumpărării, achiziției intracomunitare, importului, închirierii sau leasingului, plus cheltuielile legate de acel vehicul. Restricția nu se aplică vehiculelor cu masă totală maximă autorizată peste 3.500 kg sau cu peste 9 scaune — camioane și utilaje de transport greu ies din limitare.

## Ce se greșește în practică

- Se aplică automat limitarea de 50% și la mijloace fixe care nu sunt vehicule rutiere motorizate (utilaje, echipamente de producție).
- Se deduce integral TVA la un autoturism de firmă folosit și în scop personal, fără să se aplice limitarea de 50%.
- Se ignoră excepția pentru vehiculele grele (peste 3.500 kg sau peste 9 scaune), aplicându-se limitarea și acolo unde nu se justifică.
- Se introduce în decont suma brută de pe factură, fără ca limitarea de 50% (acolo unde se aplică) să fie calculată înainte, la nivel de sumă introdusă.

## Ce face iConta.eu

`calcul_d300` preia integral TVA-ul din antetul și liniile facturii, fără nicio verificare automată a tipului de bun (vehicul vs. alt mijloc fix) sau a flag-ului de utilizare exclusiv economică — limitarea de 50% pentru vehicule nu e un gard automat în motorul de calcul. Ea trebuie aplicată manual de contabil înainte ca factura să ajungă în decont: dacă vehiculul nu e utilizat exclusiv economic, doar 50% din TVA trebuie introdus efectiv ca sumă deductibilă, aplicația nu face această distincție singură.

[iConta.eu](/)
