---
title: "Nota de recepție la bunurile primite în custodie"
description: "Când e obligatorie Nota de recepție și constatare de diferențe pentru bunurile pe care firma le primește spre păstrare sau prelucrare, fără să le dețină."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Nota de recepție la bunurile primite în custodie

O firmă poate primi bunuri care nu-i aparțin — spre prelucrare, păstrare sau custodie — și care nu trebuie confundate, în evidență, cu propriile stocuri. Documentul care marchează corect intrarea acestor bunuri e același NIR folosit la achizițiile obișnuite, dar cu o particularitate: aici e obligatoriu prin lege, nu opțional.

## Temeiul legal

::: ghid-temei
„Nota de recepție și constatare de diferențe (NIR) servește ca: - document pentru recepția bunurilor aprovizionate; - document justificativ pentru încărcare în gestiune; - document justificativ de înregistrare în contabilitate. Nota de recepție și constatare de diferențe se folosește ca document de recepție obligatoriu numai în cazul: - bunurilor materiale cuprinse într-o factură sau aviz de însoțire a mărfii, care fac parte din gestiuni diferite; - bunurilor materiale primite spre prelucrare, în custodie sau în păstrare; - bunurilor materiale procurate de la persoane fizice; - bunurilor materiale care sosesc neînsoțite de documente de livrare; - bunurilor materiale care prezintă diferențe la recepție; - mărfurilor intrate în gestiunile la care evidența se ține la preț de vânzare."
— OMFP nr. 2634/2015, Anexa 2, Grupa a III-a, Cod 14-3-1A (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Ce înseamnă practic pentru bunurile primite în custodie:

- **NIR-ul e obligatoriu**, explicit — bunurile primite spre prelucrare, custodie sau păstrare sunt unul dintre cele șase cazuri enumerate în care întocmirea lui nu e opțională, indiferent dacă bunurile respective sunt sau nu însoțite de factură.
- Evidența acestor bunuri trebuie ținută **separat** de bunurile proprii ale firmei — norma prevede explicit, pentru fișele de magazie, că „pentru valori materiale primite spre prelucrare de la terți sau în custodie se întocmesc fișe distincte, care se țin separat de cele aferente propriilor valori materiale".
- La inventariere, bunurile primite în custodie sau consignație se inventariază **separat** de bunurile proprii ale entității, iar o copie a listei de inventariere se transmite entității care deține efectiv bunurile respective.

## Ce se greșește în practică

- Se recepționează bunurile în custodie direct pe baza documentului de transport al proprietarului, fără NIR propriu, considerându-se că „nu sunt ale firmei, deci nu se justifică documentul" — legea cere exact contrariul: tocmai pentru că nu sunt ale firmei e nevoie de un document clar de constatare.
- Se amestecă evidența bunurilor în custodie cu stocurile proprii, în aceleași fișe de magazie — norma cere fișe distincte, separate.
- Se omite trimiterea unei copii a listei de inventariere către entitatea proprietară a bunurilor, la inventarierea anuală — obligație explicită pentru bunurile primite în custodie sau consignație.

## Ce face iConta.eu

Verificat în cod: modulele `core/stocuri.py`, `core/stocuri_api.py` și `core/stocuri_cv.py` gestionează evidența de stocuri a firmei pe baza documentelor de intrare/ieșire înregistrate. Nu am găsit în aceste module o categorie sau un flux distinct pentru „bunuri primite în custodie" separat de stocurile proprii ale firmei — evidența separată a bunurilor primite spre prelucrare, custodie sau păstrare, cerută de OMFP nr. 2634/2015, rămâne, la acest moment, în sarcina contabilului, organizată în afara fluxului standard de stocuri al aplicației.

[iConta.eu](/)
