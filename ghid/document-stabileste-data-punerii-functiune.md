---
title: "Ce document stabilește data punerii în funcțiune a unui mijloc fix?"
description: "Momentul de la care începe amortizarea fiscală a unui mijloc fix și legătura lui cu data punerii în funcțiune, conform Codului fiscal și Catalogului mijloacelor fixe."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce document stabilește data punerii în funcțiune a unui mijloc fix?

Data punerii în funcțiune (PIF) a unui mijloc fix este momentul de referință de la care se calculează amortizarea fiscală — nu data facturii, nu data recepției mărfii, ci data de la care activul este efectiv folosit în activitate.

## Temeiul legal

::: ghid-temei
„Amortizarea fiscală se calculează după cum urmează:
a) începând cu luna următoare celei în care mijlocul fix amortizabil se pune în funcțiune, prin aplicarea regimului de amortizare prevăzut la alin. (5)."
— Legea 227/2015 (Codul fiscal), art. 28 alin. (12) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Codul fiscal ancorează momentul de start al amortizării de „punerea în funcțiune", dar nu numește un formular unic care să ateste acest moment — practica se sprijină pe două tipuri de documente, în funcție de situație:

- Pentru active care necesită montaj/instalare sau recepție tehnică, documentul uzual este **procesul-verbal de recepție/punere în funcțiune**, întocmit de o comisie internă sau de comun acord cu furnizorul/executantul.
- Pentru imobilizările în curs de execuție (investiții realizate în regie proprie sau prin antrepriză), reglementările contabile prevăd explicit că acestea „se trec în categoria imobilizărilor finalizate după recepția, darea în folosință sau punerea în funcțiune a acestora" (OMFP 1802/2014, pct. 231 alin. (2)) — deci recepția/darea în folosință e momentul de transfer contabil.
- Catalogul mijloacelor fixe (HG 2139/2004) leagă de acest moment și stabilirea duratei normale de funcționare: „la punerea în funcțiune a acestui mijloc fix, se va stabili durata normală de funcționare în limitele intervalului" prevăzut de catalog.
- Amortizarea fiscală începe abia **luna următoare** celei în care are loc punerea în funcțiune, nu în luna achiziției și nici în luna PIF însăși.

## Ce se greșește în practică

- Se începe amortizarea de la data facturii de achiziție, ignorând intervalul (uneori de luni) până la instalare și PIF efectivă.
- Nu se întocmește niciun document care să ateste data PIF, iar la un control fiscal data devine imposibil de dovedit altfel decât prin data facturii — nefavorabilă contribuabilului dacă amortizarea a fost pornită mai devreme.
- Se confundă data recepției mărfii (NIR) cu data punerii în funcțiune — pentru echipamente care necesită montaj, cele două date pot diferi cu săptămâni sau luni.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **înregistrează data punerii în funcțiune** ca dată introdusă de contabil la fiecare mijloc fix (câmpul `data_pif` din `core/repo_mijloace_fixe.py` și `core/mijloace_fixe_import_api.py`) și o folosește pentru a determina de când începe amortizarea. Aplicația **nu generează și nu solicită** procesul-verbal de recepție/punere în funcțiune ca document justificativ — data se preia ca atare din fișierul de import sau din introducerea manuală, fără o verificare automată față de un document sursă.

[iConta.eu](/)
