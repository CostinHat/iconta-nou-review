---
title: Comisionul bancar este deductibil la PFA?
description: Da — comisioanele și alte servicii bancare sunt cheltuieli deductibile expres numite prin normele metodologice ale Codului fiscal, cu condiția să fie justificate prin documente și legate de activitatea PFA-ului.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Comisionul bancar este deductibil la PFA?

Da, și e unul dintre puținele cazuri de deductibilitate cu temei explicit, numit direct în textul legii — nu o interpretare pe baza unei clauze generale. Comisioanele bancare pentru contul folosit în activitate se deduc integral, dacă respectă condițiile generale de deductibilitate.

## Temeiul legal

::: ghid-temei
HG 1/2016 (Norme metodologice), pct. 7 alin. (5): listă exemplificativă de cheltuieli deductibile — "e) dobânzile aferente creditelor bancare; f) cheltuielile cu comisioanele și cu alte servicii bancare; ... n) cheltuielile cu amortizarea, în conformitate cu prevederile art. 28 din Codul fiscal, după caz; ... w) alte cheltuieli efectuate în scopul realizării veniturilor."

Codul fiscal, art. 68 alin. (4): condiții generale de deductibilitate — "a) să fie efectuate în cadrul activităților independente, justificate prin documente; b) să fie cuprinse în cheltuielile exercițiului financiar al anului în cursul căruia au fost plătite; ... j) să fie efectuate în scopul desfășurării activității și reglementate prin acte normative în vigoare ..."
:::

## Comision bancar = deductibilitate directă, nu prin analogie

Spre deosebire de comisioanele reținute de procesatori de plăți nebancari, comisionul bancar are un temei numit explicit: litera f) de la pct. 7 alin. (5) din normele metodologice îl citează textual ca "cheltuieli cu comisioanele și cu alte servicii bancare". Condiția rămâne, ca la orice cheltuială, ca sumele să fie legate de contul/activitatea PFA-ului și justificate prin documentul bancar (extras de cont, notă de taxare).

::: ghid-exemplu
Un PFA plătește lunar 15 lei comision de mentenanță cont curent și, ocazional, comision de transfer intern de 5 lei. Ambele sume se înregistrează ca plăți, categoria "cheltuiala_deductibila", cu explicația "comision bancar" și documentul justificativ extrasul de cont pe luna respectivă.
:::

## Ce se greșește în practică

- Se lasă comisionul bancar "ascuns" în soldul net din extras, fără să fie înregistrat separat ca plată/cheltuială deductibilă.
- Se încadrează comisionul din greșeală la "cheltuială nedeductibilă", din confuzie cu alte tipuri de taxe bancare (de exemplu penalități de întârziere la un credit, care nedeductibile sunt).
- Nu se păstrează extrasul de cont ca document justificativ pentru fiecare comision dedus.
- Se deduce comisionul unui cont personal, folosit ocazional și pentru activitatea PFA, fără nicio delimitare — condiția de la art. 68 alin. (4) lit. a) cere ca cheltuiala să fie efectuată "în cadrul activităților independente".

## Ce face iConta.eu

Comisionul bancar se înregistrează ca operațiune de plată, în categoria `cheltuiala_deductibila` din `CATEGORII_PLATA = {"cheltuiala_deductibila", "cheltuiala_limitata", "cheltuiala_nedeductibila", "aport_retragere", "rambursare_credit"}` (`core/rip_api.py`). Validarea (`_valideaza`) cere deductibilitate explicită pentru orice plată de tip `cheltuiala*`. Mai mult, funcția `import_banca` generează automat ciorne din extrasul bancar (`extras_linii`), cu categorie și deductibilitate propuse implicit ca "cheltuiala_deductibila"/"integral" — propunere pe care contabilul o confirmă sau o corectează înainte de validare, așa cum cere explicit comentariul din cod.

[iConta.eu](/)
