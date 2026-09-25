---
title: "Puncte de vedere ANAF privind dividendele 2026"
description: "Regula legală în vigoare din 2026 pentru impozitul pe dividende — cota de 16% și cum se stabilește data de la care se aplică."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Puncte de vedere ANAF privind dividendele 2026

În 2026 s-a schimbat semnificativ regimul de impozitare a dividendelor: cota a crescut de la 10% la 16%, iar momentul care contează pentru stabilirea cotei aplicabile nu mai este data plății, ci data distribuirii. Nu există un document unic, oficial, intitulat „puncte de vedere ANAF privind dividendele" — ce poate fi documentat cu certitudine este cadrul legal aplicat, care e sursa oricărei interpretări sau clarificări ulterioare a ANAF.

## Temeiul legal

::: ghid-temei
„Impozitul pe dividende se stabilește prin aplicarea unei cote de impozit de 16% asupra dividendului brut plătit unei persoane juridice române. Impozitul pe dividende se declară și se plătește la bugetul de stat, până la data de 25 inclusiv a lunii următoare celei în care se plătește dividendul."
— Legea nr. 227/2015 privind Codul fiscal, art. 43 alin. (2), astfel cum a fost modificat de Legea nr. 141/2025 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Cota de **16%** se aplică dividendelor distribuite **începând cu 1 ianuarie 2026** (Legea 141/2025, art. VII alin. (1) lit. a)).
- Excepție tranzitorie: pentru dividendele distribuite pe baza situațiilor financiare interimare întocmite în 2025, cota rămâne **10%**, „fără recalcularea impozitului [...] după regularizarea acestora pe baza situațiilor financiare anuale aferente exercițiului financiar 2025" (Legea 141/2025, art. VII alin. (2)).
- Dacă dividendele distribuite nu au fost plătite până la sfârșitul anului în care s-a aprobat distribuirea, impozitul se plătește „până la data de 25 ianuarie a anului următor" (art. 43 alin. (3)).
- Cota de 16% se aplică deopotrivă persoanelor juridice care plătesc dividende către alte persoane juridice române (art. 43) și persoanelor fizice beneficiare, care sunt impozitate „cu o cotă de 16% din suma acestora, impozitul fiind final" (art. 97).

## Ce se greșește în practică

- Se aplică cota veche de 10% pentru dividende distribuite după 1 ianuarie 2026, confundând data distribuirii cu data plății.
- Se recalculează impozitul pentru dividendele interimare distribuite în 2025, deși legea prevede explicit că nu se face recalculare la regularizare.
- Se calculează cota după data la care banii ajung efectiv la asociat, nu după data la care s-a înregistrat contabil distribuirea (creditul contului 457).
- Se omite termenul special de plată (25 ianuarie anul următor) pentru dividendele aprobate dar neplătite până la finalul anului.

## Ce face iConta.eu

iConta.eu **calculează impozitul pe dividende cu regula corectă pentru tranziția 2025→2026**: modulul dedicat atribuie plățile de dividende pe distribuiri, în ordine cronologică (FIFO), astfel încât impozitul să se aplice cu cota valabilă la **data distribuirii**, nu la data plății — exact mecanismul cerut de art. VII din Legea 141/2025 (16% pentru distribuirile din 2026, 10% pentru cele interimare din 2025, fără recalculare). Această logică e folosită atât la generarea declarației D205, cât și la reconcilierea ei internă, ceea ce reduce riscul de a aplica din greșeală cota veche pentru distribuiri făcute deja sub noul regim.

[iConta.eu](/)
