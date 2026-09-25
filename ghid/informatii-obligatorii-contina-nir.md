---
title: "Ce informații obligatorii trebuie să conțină un NIR?"
description: "Câmpurile obligatorii ale Notei de recepție și constatare de diferențe (NIR), cod 14-3-1A, conform OMFP 2634/2015, și situațiile în care întocmirea ei este obligatorie."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce informații obligatorii trebuie să conțină un NIR?

Nota de recepție și constatare de diferențe (NIR) nu este necesară la fiecare intrare de marfă — legea o impune doar în situații specifice. Când e obligatorie, formularul are un set fix de câmpuri, stabilit prin modelul-cadru aprobat de Ministerul Finanțelor.

## Temeiul legal

::: ghid-temei
„(Cod 14-3-1A) Nota de recepție și constatare de diferențe (NIR) servește ca: document pentru recepția bunurilor aprovizionate; document justificativ pentru încărcare în gestiune; document justificativ de înregistrare în contabilitate. Nota de recepție și constatare de diferențe se folosește ca document de recepție obligatoriu numai în cazul: bunurilor materiale cuprinse într-o factură sau aviz de însoțire a mărfii, care fac parte din gestiuni diferite; bunurilor materiale primite spre prelucrare, în custodie sau în păstrare; bunurilor materiale procurate de la persoane fizice; bunurilor materiale care sosesc neînsoțite de documente de livrare; bunurilor materiale care prezintă diferențe la recepție; mărfurilor intrate în gestiunile la care evidența se ține la preț de vânzare."
— OMFP nr. 2.634/2015 privind documentele financiar-contabile, Anexa 2 — Norme specifice de întocmire și utilizare a documentelor financiar-contabile (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Câmpurile pe care modelul oficial (cod 14-3-1A) le impune, conform anexei cu modele:

- numărul și data documentului, plus numărul facturii/avizului de însoțire a mărfii;
- datele privind expedierea (vagon/auto, delegat, documente însoțitoare);
- pentru fiecare bun recepționat: denumire, U/M, cantitate conform documentelor, cantitate recepționată, preț unitar, valoare;
- eventualele **diferențe** constatate la recepție (plus/minus), cu cantitate, preț unitar și valoare;
- semnăturile membrilor comisiei de recepție și ale persoanei care primește bunurile în gestiune, cu data.

În cazurile în care NIR-ul **nu** este obligatoriu (bunuri de la același furnizor, aceeași gestiune, fără diferențe), recepția și înregistrarea în contabilitate se fac direct pe baza documentului de livrare (factură sau aviz de însoțire).

## Ce se greșește în practică

- Se întocmește NIR pentru orice intrare de marfă, chiar și atunci când legea nu o impune, dublând inutil documentele justificative.
- Se omite întocmirea NIR-ului tocmai în cazurile în care e obligatoriu — cel mai frecvent, la mărfuri procurate de la persoane fizice sau la bunuri sosite neînsoțite de documente de livrare.
- Se lasă necompletate datele valorice pe NIR, fără să se asigure că acestea apar în alt document justificativ care stă la baza înregistrării în contabilitate — condiție cerută explicit de normă atunci când valorile nu se înscriu direct pe NIR.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează NIR-ul din modulul de stocuri pe baza articolelor introduse, validând că fiecare linie are denumire, cantitate pozitivă și cotă de TVA declarată explicit — o linie de NIR fără articole este respinsă de motorul intern, nefiind considerată o recepție validă. Decizia dacă un NIR este obligatoriu pentru o anumită intrare de marfă (conform situațiilor enumerate mai sus) rămâne o evaluare a utilizatorului.

[iConta.eu](/)
