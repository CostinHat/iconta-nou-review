---
title: "TVA la import: când devine exigibilă"
description: Exigibilitatea TVA la import e legată de exigibilitatea taxelor vamale, nu de data facturii sau a plății — un reper strict legal, pe care aplicația nu îl calculează sau afișează.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# TVA la import: când devine exigibilă

La import, exigibilitatea TVA nu se stabilește după data facturii furnizorului extern și nici după data la care firma plătește efectiv la vamă. Legea o leagă de un alt reper: momentul la care devin exigibile taxele vamale (sau ar deveni, dacă bunul le-ar fi supus).

## Temeiul legal

::: ghid-temei
„(1) În cazul în care, la import, bunurile sunt supuse taxelor vamale, taxelor agricole sau altor taxe europene similare, stabilite ca urmare a unei politici comune, faptul generator și exigibilitatea taxei pe valoarea adăugată intervin la data la care intervin faptul generator și exigibilitatea respectivelor taxe europene.
(2) În cazul în care, la import, bunurile nu sunt supuse taxelor europene prevăzute la alin. (1), faptul generator și exigibilitatea taxei pe valoarea adăugată intervin la data la care ar interveni faptul generator și exigibilitatea acelor taxe europene dacă bunurile importate ar fi fost supuse unor astfel de taxe.
(3) În cazul în care, la import, bunurile sunt plasate într-un regim vamal special, prevăzut la art. 295 alin. (1) lit. a) și d), faptul generator și exigibilitatea taxei intervin la data la care acestea încetează a mai fi plasate într-un astfel de regim."

— Codul fiscal (Legea 227/2015 consolidat), art. 285
:::

Pe scurt: dacă bunul e supus taxelor vamale, exigibilitatea TVA "urmează" exigibilitatea taxei vamale (alin. 1). Dacă bunul nu e supus taxelor vamale (de exemplu are tarif vamal 0%), exigibilitatea TVA se stabilește tot la data la care ar fi devenit exigibilă o taxă vamală ipotetică, dacă bunul ar fi fost supus uneia (alin. 2) — practic, tot data la care bunul intră efectiv sub regimul vamal de import. Dacă bunul e plasat într-un regim vamal special (de exemplu antrepozit vamal), exigibilitatea se amână până când bunul iese din acel regim (alin. 3).

## Ce se greșește în practică

- Se confundă exigibilitatea TVA cu data facturii emise de furnizorul din afara UE — factura externă nu are relevanță pentru exigibilitatea TVA la import.
- Se confundă exigibilitatea cu data plății efective la vamă, deși legea o leagă de exigibilitatea taxelor vamale (sau a echivalentului lor ipotetic), nu de momentul plății.
- Se ignoră cazul bunurilor plasate într-un regim vamal special (alin. 3), unde exigibilitatea TVA se amână până la ieșirea din regim, nu se calculează de la data intrării fizice a bunului în țară.

## Ce face iConta.eu

Motorul de calcul al importului (`core/import_export.py`) determină baza de TVA (valoare vamală + taxe + accesorii) și taxa datorată pe baza sumelor și a cotei introduse de contabil, dar **nu are niciun câmp sau logică legată de dată sau de exigibilitate** — funcția de calcul primește doar sume și o cotă, nu o dată a operațiunii. Stabilirea momentului exigibilității, conform art. 285, rămâne integral în sarcina contabilului, pe baza documentelor vamale ale operațiunii concrete; aplicația nu calculează și nu afișează această dată.

[iConta.eu](/)
