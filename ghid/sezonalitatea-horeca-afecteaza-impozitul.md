---
title: "Sezonalitatea în HoReCa: cum afectează impozitul"
description: "Din 2026, cota de impozit pe veniturile microîntreprinderilor e unică, 1% — vechiul split 1%/3% pe coduri CAEN și pragul de 60.000 euro au fost abrogate. Ce mai contează pentru un HoReCa sezonier e doar pragul de 100.000 euro."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Sezonalitatea în HoReCa: cum afectează impozitul

Restaurantele, barurile și unitățile de cazare au, prin natura activității, venituri concentrate pe câteva luni ale anului. Până la finalul lui 2025, această sezonalitate putea schimba, în cursul anului fiscal, cota de impozit a microîntreprinderii (de la 1% la 3%, pentru firmele cu coduri CAEN specifice HoReCa sau peste un prag de 60.000 euro). **Începând cu 1 ianuarie 2026, acest mecanism a fost abrogat**: cota e unică, 1%, indiferent de codul CAEN sau de cifra de afaceri sub 100.000 euro. Ce rămâne relevant pentru sezonalitate e doar riscul de a depăși, într-un trimestru bogat, pragul de 100.000 euro care scoate firma din regimul micro și o trece la impozit pe profit.

## Temeiul legal

::: ghid-temei
„(1) Cota de impozit pe veniturile microîntreprinderilor este de 1%."
— Legea 227/2015 (Codul fiscal), art. 51 alin. (1), în forma modificată de OUG 89/2025, în vigoare de la 1 ianuarie 2026 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„4. La articolul 51, alineatul (1) se modifică și va avea următorul cuprins: (1) Cota de impozit pe veniturile microîntreprinderilor este de 1%. [...] 5. La articolul 51, alineatele (1^1) și (4^1)-(4^3) se abrogă."
— OUG 89/2025, art. I pct. 4-5 — actul care a eliminat cota de 3% (fostul alin. (1^1)) și pragul de 60.000 euro/lista de coduri CAEN (fostul alin. (4^1)) din art. 51 al Codului fiscal (sursă: anaf_surse/oug_89_2025.txt)

„(1) Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit începând cu trimestrul în care s-a depășit această limită."
— Legea 227/2015 (Codul fiscal), art. 52 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Consecințele practice pentru un HoReCa sezonier, în 2026:

- **Nu mai există cotă de 3%** și nici lista de coduri CAEN (restaurante, baruri, hoteluri, cazare) care declanșa acea cotă — OUG 89/2025 a abrogat integral fostele alin. (1^1) și (4^1)-(4^3) ale art. 51, care conțineau acest mecanism. Din 1 ianuarie 2026, toate microîntreprinderile plătesc **1%**, indiferent de activitate.
- Ce contează în continuare pentru o firmă sezonieră e **pragul de 100.000 euro** de la art. 52 alin. (1): dacă veniturile cumulate de la 1 ianuarie depășesc acest prag într-un trimestru (de exemplu, un sezon de vară foarte bun), firma **iese din regimul micro** și datorează impozit pe profit (16%, pe bază de venituri minus cheltuieli deductibile) începând cu trimestrul depășirii — nu doar o cotă mai mare în cadrul regimului micro.
- Trecerea la impozit pe profit se face **de la trimestrul depășirii**, nu retroactiv, dar rămâne valabilă până la sfârșitul anului fiscal, chiar dacă veniturile scad din nou în extrasezon.
- Limitele fiscale se verifică pe baza **veniturilor înregistrate cumulat de la începutul anului fiscal**, la cursul de schimb valabil la închiderea exercițiului financiar precedent (art. 52 alin. (5), modificat tot prin OUG 89/2025).

## Ce se greșește în practică

- Se aplică în continuare, din obișnuință sau din șabloane vechi, cota de 3% pentru activitățile HoReCa — mecanismul a fost abrogat de la 1 ianuarie 2026; în 2026 toate microîntreprinderile plătesc 1%.
- Se calculează pragul de 100.000 euro doar pe luna sau trimestrul curent, ignorând caracterul cumulat de la începutul anului — un sezon foarte bun poate scoate firma din regimul micro chiar dacă anul, în ansamblu, ar fi fost sub prag.
- Se confundă „ieșirea din regimul micro" (trecere la impozit pe profit, 16% pe bază netă) cu o simplă schimbare de cotă în cadrul regimului micro — sunt regimuri fiscale diferite, cu baze de calcul diferite.

## Ce face iConta.eu

La data acestui ghid, iConta.eu aplică, pentru regimul micro, cota unică de 1% conform art. 51 alin. (1) din Codul fiscal (`core/common.py`, registrul de cote „impozit_micro"), fără nicio diferențiere pe cod CAEN — în acord cu abrogarea, din 2026, a fostei cote de 3%. Aplicația **nu determină automat** trimestrul din care o firmă sezonieră depășește pragul de 100.000 euro și trece la impozit pe profit — aceasta rămâne o verificare pe care contabilul o face pe baza evidenței contabile generale oferite de aplicație.

[iConta.eu](/)
