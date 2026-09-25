---
title: "Diferențe de inventar la numerar 2026: cauze"
description: "De ce apar diferențe între monetarul din casierie, registrul de casă și evidența contabilă la inventarierea numerarului, și cum se documentează constatarea."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Diferențe de inventar la numerar 2026: cauze

O diferență de numerar la inventariere nu apare niciodată izolat — ea e mereu diferența dintre trei surse care, în mod normal, ar trebui să coincidă: numerarul numărat fizic (monetarul), soldul din registrul de casă și soldul din evidența contabilă.

## Temeiul legal

::: ghid-temei
„Disponibilitățile în lei și în valută din casieria entității se inventariază în ultima zi lucrătoare a exercițiului financiar, după înregistrarea tuturor operațiunilor de încasări și plăți privind exercițiul respectiv, confruntându-se soldurile din registrul de casă cu monetarul și cu cele din contabilitate." — OMFP 2861/2009, Anexa 1, pct. 29 alin. (3) (sursă: anaf_surse/omfp_2861_2009.txt)
:::

Legea cere explicit o confruntare **în trei**, nu doar între două surse — de aici și cea mai frecventă cauză reală a unei „diferențe": nu neapărat un plus sau un minus fizic de bani, ci faptul că una din cele trei surse n-a fost actualizată corect înainte de numărătoare.

Cauzele concrete întâlnite cel mai des:

- **Operațiuni neînregistrate la momentul lor** — o încasare sau o plată efectuată dar netrecută încă în registrul de casă la data inventarierii, ceea ce face ca soldul din registru să nu corespundă cu monetarul, deși niciun ban nu lipsește real.
- **Erori de numărare sau de calcul** — bancnote/monede numărate greșit, o adunare greșită a monetarului sau a soldului din registru.
- **Diferențe reale de casierie** — lipsă sau plus de numerar efectiv, care poate fi imputabilă casierului sau altei persoane responsabile, sau poate rămâne neimputabilă.
- **Documente justificative lipsă sau întârziate** — o plată făcută fără chitanță/bon corespunzător, înregistrată ulterior, care rupe temporar corelarea celor trei surse.
- **Decalaj de curs valutar**, pentru numerarul deținut în valută — evaluarea disponibilului valutar la cursul de la data inventarierii poate produce o diferență contabilă față de valoarea înregistrată anterior, distinctă de o diferență fizică de numerar.

## Ce se greșește în practică

- Se tratează orice diferență ca fiind automat o lipsă sau un plus fizic de bani, fără să se verifice mai întâi dacă nu e doar o operațiune neînregistrată la timp.
- Se face confruntarea doar între două din cele trei surse cerute de normă (de exemplu doar monetar vs. registru, fără contabilitate), ceea ce poate ascunde o diferență reală sau, invers, poate semnala una inexistentă.
- Se omite documentarea constatării printr-un proces-verbal, deși rezultatul inventarierii — inclusiv o diferență de casierie — trebuie înregistrat în contabilitate potrivit reglementărilor aplicabile.

## Ce face iConta.eu

Aici e important de spus onest ce nu face aplicația. Ecranul „Inventariere anuală" din iConta.eu e construit pentru stocuri (operațiile „Plus stoc"/„Minus", cu conturi acceptate explicit: 371, 301, 302, 303, 345, 381) și pentru mijloace fixe („Plus mijloc fix"/„Casare") — niciun cont de disponibilități (5311/5314) nu se regăsește printre conturile acceptate de acest formular. O diferență constatată la inventarierea casieriei nu se poate înregistra prin acest ecran; înregistrarea contabilă a plusului sau minusului de casă rămâne o notă contabilă separată, introdusă manual.

Separat, în ecranul de registru de casă al aplicației, orice operațiune de tip încasare/plată se poate introduce fără limită inferioară pe soldul rezultat — aplicația nu calculează soldul rulant înainte de o nouă înregistrare și nu semnalează dacă acesta ar deveni negativ. Practic, iConta nu poate detecta singură, în timp real, momentul în care apare o cauză tipică de diferență (o operațiune introdusă cu întârziere) — confruntarea celor trei surse, cerută de normă, rămâne responsabilitatea contabilului, la finalul exercițiului.

[iConta.eu](/)
