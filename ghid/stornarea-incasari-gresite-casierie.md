---
title: "Stornarea unei încasări greșite la casierie"
description: "De ce o chitanță sau o dispoziție de încasare întocmită greșit nu se corectează prin ștersătură, ci se anulează, conform normelor privind documentele financiar-contabile."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Stornarea unei încasări greșite la casierie

O sumă încasată greșit la casierie — client greșit, sumă greșită, operațiune dublată — nu se remediază prin tăierea cifrei și scrierea alteia deasupra, așa cum se procedează la majoritatea documentelor contabile. Documentele de casă au un regim special, mai strict.

## Temeiul legal

::: ghid-temei
„15. În cazul documentelor financiar-contabile la care nu se admit corecturi, cum sunt cele pe baza cărora se primește, se eliberează sau se justifică numerarul, ori al altor documente pentru care normele de utilizare prevăd asemenea restricții, documentul întocmit greșit se anulează și se păstrează sau rămâne în carnetul respectiv. La corectarea documentului justificativ în care se consemnează operații de predare-primire a valorilor materiale și a mijloacelor fixe este necesară confirmarea, prin semnătură, atât a predătorului, cât și a primitorului."
— OMFP nr. 2.634/2015, Anexa 1 (Norme generale de întocmire și utilizare a documentelor financiar-contabile), pct. 15 (sursă: anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt)
:::

Aplicat la o încasare greșită la casierie, mecanismul e simplu, dar diferit de corectarea unei note contabile obișnuite:

- Chitanța sau dispoziția de încasare întocmită greșit **nu se corectează prin ștersătură** — spre deosebire de regula generală de la pct. 14 din aceleași norme, care permite corectarea prin tăierea textului greșit și înscrierea celui corect. Documentele de casă intră explicit în excepția de la pct. 15.
- Documentul greșit **se anulează** (se marchează vizibil ca anulat) și **se păstrează în carnetul respectiv** — nu se rupe și nu se aruncă; exemplarele anulate rămân în evidență pentru control.
- Se întocmește un document nou, corect, pentru operațiunea reală.
- Dacă eroarea a fost deja înregistrată în contabilitate (nota de contabilitate a fost făcută pe baza chitanței greșite), corectarea rulajului contabil se face prin stornare — potrivit pct. 20 din aceleași norme, pe documentul inițial se menționează numărul și data notei de contabilitate prin care s-a efectuat stornarea, iar în nota de stornare se menționează documentul, data și numărul de ordine ale operațiunii stornate.

## Ce se greșește în practică

- Se corectează chitanța de casă prin tăierea sumei greșite și scrierea celei corecte deasupra, ca la orice alt document, ignorând regimul special de la pct. 15.
- Documentul anulat este rupt sau aruncat, în loc să rămână în carnet ca dovadă a anulării, pentru control ulterior.
- Se corectează doar documentul de casă, fără să se stornez și înregistrarea contabilă deja făcută pe baza lui, lăsând o discrepanță între registrul de casă și jurnalul contabil.

## Ce face iConta.eu

La data acestui ghid, iConta.eu gestionează registrul de casă și mișcările de numerar prin modulul `core/casa.py` (funcțiile `registru_casa`, `sold_final`, `verifica_plafon`, `regula_cont_casa`), care calculează soldurile și verifică plafonul de casă, dar **nu are o funcție dedicată de „anulare" a unei chitanțe/dispoziții de încasare** care să reproducă mecanismul de la pct. 15 (document păstrat, marcat anulat, cu unul nou emis în loc). Corectarea unei încasări greșite — anularea documentului fizic și, dacă e cazul, stornarea notei contabile aferente — se face manual, prin înregistrările pe care contabilul le introduce în aplicație.

[iConta.eu](/)
