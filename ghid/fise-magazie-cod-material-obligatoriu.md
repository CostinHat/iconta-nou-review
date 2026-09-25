---
title: "Fișe de magazie pe cod de material: obligatoriu"
description: "Ce spun normele contabile despre fișa de magazie (cod 14-3-8): pe fiecare fel de material, document cu document, nu evidență agregată."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Fișe de magazie pe cod de material: obligatoriu

Fișa de magazie este unul dintre documentele financiar-contabile cu regim reglementat explicit de normele Ministerului Finanțelor — inclusiv modul în care trebuie organizată evidența, pe fiecare fel de material.

## Temeiul legal

::: ghid-temei
„FIȘĂ DE MAGAZIE (Cod 14-3-8) Fișa de magazie servește ca document de evidență a intrărilor, ieșirilor și stocurilor de bunuri materiale. Fișele de magazie se țin pe fiecare loc de depozitare a valorilor materiale, pe feluri de materiale, ordonate pe conturi, grupe, eventual subgrupe, sau în ordine alfabetică. Pentru valori materiale primite spre prelucrare de la terți sau în custodie se întocmesc fișe distincte, care se țin separat de cele aferente propriilor valori materiale. Înregistrările în fișele de magazie se fac document cu document."
— OMFP nr. 2.634/2015 (Norme specifice de utilizare a documentelor financiar-contabile, Anexa nr. 2) (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Ce rezultă din text pentru gestiunea de stocuri:

- Fișa de magazie se ține **pe fiecare fel de material** (deci pe cod de material, practic) și **pe fiecare loc de depozitare** — o evidență agregată, pe categorii largi de produse, nu respectă norma.
- Materialele primite de la terți spre prelucrare sau în custodie primesc **fișe separate**, distincte de cele ale propriilor stocuri — amestecarea lor într-o singură evidență e o abatere de la normă.
- Înregistrările se fac **document cu document** (pe fiecare notă de recepție, bon de consum etc.), nu prin însumări periodice ulterioare.

## Ce se greșește în practică

- Se ține o singură fișă de magazie „pe categorie de produse" (de exemplu, „materiale de birou"), în loc de o fișă distinctă pentru fiecare fel de material, cu cod propriu.
- Se amestecă în aceeași fișă bunurile proprii cu cele primite spre prelucrare sau în custodie de la terți, deși norma cere fișe separate.
- Se actualizează fișa de magazie prin totaluri lunare, nu document cu document, ceea ce face imposibilă reconstituirea exactă a mișcărilor la o inventariere sau la un control.

## Ce face iConta.eu

Verificat în cod: `core/stocuri.py` și `core/repo_stocuri.py` țin evidența mișcărilor de stoc pe fiecare articol (cod de material), cu mișcări de intrare/ieșire distincte, iar `core/d406_stocuri.py` calculează soldurile de deschidere/închidere per articol pentru raportarea SAF-T la cerere ANAF — structura urmează, la nivel de aplicație, principiul „pe fel de material" din normă, deși aplicația nu generează formularul tipizat „Fișă de magazie" (cod 14-3-8) ca document separat.

[iConta.eu](/)
