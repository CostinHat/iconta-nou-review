---
title: "Ce faci dacă la inventar lipsește un mijloc fix?"
description: "Procedura legală pentru un mijloc fix constatat lipsă la inventarierea anuală: imputare la valoarea de înlocuire, cu explicații scrise de la gestionar."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce faci dacă la inventar lipsește un mijloc fix?

O lipsă constatată la inventarierea anuală nu se rezolvă printr-o simplă notă contabilă de scădere — legea cere o procedură cu pași expliciți: explicații scrise de la persoana responsabilă, stabilirea naturii lipsei de către comisia de inventariere și, dacă lipsa e imputabilă, recuperarea ei la valoarea de înlocuire, nu la valoarea contabilă rămasă.

## Temeiul legal

::: ghid-temei
„(2) În cazul constatării unor lipsuri imputabile în gestiune, administratorii trebuie să impute persoanelor vinovate bunurile lipsă la valoarea lor de înlocuire."
— OMFP 2861/2009, pct. 40 alin. (2) (sursă: anaf_surse/omfp_2861_2009.pdf)
:::

Ce cere legea, pas cu pas:

- **Comisia de inventariere solicită explicații scrise** de la persoana care răspunde de gestionarea bunului respectiv, pentru orice lipsă constatată.
- **Se stabilește natura lipsei** — imputabilă unei persoane vinovate sau nu — pe baza explicațiilor primite și a documentelor analizate, iar comisia propune modul de regularizare a diferenței dintre datele din contabilitate și cele faptice.
- **Dacă lipsa e imputabilă**, administratorii trebuie să impute persoanei vinovate bunul lipsă la **valoarea de înlocuire** — costul de achiziție al unui bun cu caracteristici și grad de uzură similare, la data constatării, nu valoarea contabilă rămasă neamortizată a mijlocului fix.
- **Dacă lipsa nu e imputabilă** (de exemplu, o cauză justificată obiectiv), bunul se evaluează și se înregistrează în contabilitate la valoarea contabilă, fără imputare.
- Pentru lipsuri care ar putea constitui infracțiuni (sustragere), legea obligă la sesizarea organelor de urmărire penală.

## Ce se greșește în practică

- Se scade direct din evidență mijlocul fix lipsă, fără explicațiile scrise cerute de la gestionar și fără decizia comisiei de inventariere asupra naturii lipsei.
- Se impută lipsa la valoarea contabilă rămasă (neamortizată) a mijlocului fix, în loc de valoarea de înlocuire, care poate fi semnificativ diferită, mai ales pentru bunuri cu prețuri de piață în creștere.
- Se compensează automat o lipsă cu un plus constatat la alt bun, fără să fie îndeplinite condițiile legale de compensare (risc de confuzie între sorturi similare, aceeași perioadă și gestiune).

## Ce face iConta.eu

Această întrebare ține de inventarierea fizică anuală a activelor și de tratamentul lipsurilor constatate — o funcționalitate distinctă de modulul de obiecte de inventar (achiziție/dare în folosință/scoatere din uz de bunuri sub pragul de mijloc fix). iConta.eu are un ecran separat, „Inventariere anuală", cu operațiile plus stoc, plus mijloc fix, minus și casare. Operația „minus" implementează exact mecanismul din OMFP 2861/2009 pct. 40 alin. (2) — imputare la valoarea de înlocuire, distinctă de valoarea contabilă, cu notă automată către salariat (4282) sau terț (461), plus TVA aferentă —, dar **numai pentru stocuri** (materii prime, materiale, mărfuri, obiecte de inventar), nu pentru mijloace fixe: câmpul „Cont stoc" acceptă doar conturi ca 301/303/371, nu conturi de imobilizări. Pentru un **mijloc fix** lipsă, ecranul oferă doar operația „casare" (identificată prin ID-ul mijlocului fix), care scoate bunul din evidență la valoarea contabilă rămasă neamortizată (28xx + 6583 = 21x) — exact baza de calcul pe care legea o exclude pentru o lipsă imputabilă. Așadar, pentru un mijloc fix constatat lipsă și imputabil, aplicația **nu calculează automat** nota de imputare la valoarea de înlocuire; contabilul trebuie să stabilească separat această valoare și să înregistreze manual nota corespunzătoare (pe același model 4282/461 = 7581 + 4427 folosit deja pentru stocuri), explicațiile scrise și decizia comisiei de inventariere rămânând, oricum, în afara aplicației.

[iConta.eu](/)
