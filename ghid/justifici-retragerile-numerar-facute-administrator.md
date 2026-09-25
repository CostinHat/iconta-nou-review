---
title: "Cum justifici retragerile de numerar făcute de administrator?"
description: "Plafonul zilnic de 5.000 lei pentru avansurile spre decontare și interdicția de a elibera numerar peste plafon, potrivit Legii nr. 70/2015 privind disciplina financiară."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum justifici retragerile de numerar făcute de administrator?

Retragerile de numerar din casieria firmei făcute de administrator (de regulă sub formă de avans spre decontare) nu sunt libere — legea disciplinei financiare fixează un plafon zilnic și interzice eliberarea de sume peste acel plafon.

## Temeiul legal

::: ghid-temei
„se pot efectua operațiuni de încasări și plăți în numerar, în următoarele condiții: [...] plăți din avansuri spre decontare, în limita unui plafon zilnic de 5.000 lei, stabilit pentru fiecare persoană care a primit avansuri spre decontare.
[...]
Articolul 11 (1) Se interzice persoanelor prevăzute la art. 1 alin. (2) să elibereze persoanelor prevăzute la art. 1 alin. (1) și art. 8 sume în numerar peste plafonul stabilit la art. 3 alin. (1) lit. c), pe fiecare persoană și tranzacție, cu excepția operațiunilor prevăzute la art. 5."
— Legea nr. 70/2015 pentru întărirea disciplinei financiare, art. 3 alin. (1) lit. e) și art. 11 alin. (1) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Ce înseamnă acest temei pentru justificarea retragerilor administratorului:

- O sumă eliberată din casierie administratorului ca **avans spre decontare** are un plafon zilnic de **5.000 lei**, stabilit pe fiecare persoană care primește avansuri, nu pe firmă în ansamblu.
- Firma nu are dreptul să elibereze numerar peste plafon, indiferent de motiv — interdicția e adresată direct celui care face plata (art. 11 alin. (1)). **Notă de precizie:** textul art. 11 alin. (1) trimite literal la plafonul de la art. 3 alin. (1) lit. c) (plafonul general de plăți, 5.000 lei/persoană, maximum 10.000 lei/zi în total), nu la lit. e) (avansuri spre decontare) — valoarea de 5.000 lei/persoană coincide totuși la ambele litere, deci concluzia practică (plafon de 5.000 lei/persoană pe zi) rămâne aceeași.
- Justificarea reală a sumei se face ulterior prin **decont de cheltuieli**, cu documente justificative (facturi, bonuri) pentru fiecare achiziție acoperită din avans — avansul nedecontat rămâne o creanță a firmei asupra administratorului, nu o cheltuială.
- Este interzisă și **fragmentarea solicitărilor** de eliberare de numerar pentru a ocoli plafonul (art. 11 alin. (2) din aceeași lege).

## Ce se greșește în practică

- Se eliberează administratorului sume mari „cash", peste plafonul de 5.000 lei/zi, motivate ca „avans spre decontare", ceea ce încalcă direct art. 11 alin. (1).
- Se lasă avansurile nedecontate luni de zile, fără documente justificative, transformând de fapt avansul într-un împrumut informal, nereglementat ca atare.
- Se fragmentează retragerile în mai multe tranșe în aceeași zi pentru a rămâne, formal, sub plafon — practică interzisă explicit de lege.

## Ce face iConta.eu

Verificat în cod: `core/casa.py` calculează, pe baza cotei „plafon_avans_decontare" citită din nomenclatorul de cote (cu temeiul legal aferent), sumele acordate ca avans de trezorerie pe fiecare partener/persoană și generează un avertisment (`PLAFON_AVANS`) atunci când suma cumulată depășește plafonul legal; aplicația ține, de asemenea, evidența decontării avansurilor (contul 542) și a soldurilor nedecontate, dar decizia de a elibera sau nu suma peste plafon rămâne, desigur, a operatorului care introduce operațiunea de casă.

[iConta.eu](/)
