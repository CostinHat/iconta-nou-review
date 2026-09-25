---
title: "Inventarierea prin sondaj: este permisă"
description: "Cazurile în care normele de inventariere permit stabilirea stocurilor faptice prin sondaj, în locul numărării, cântăririi sau măsurării exhaustive."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Inventarierea prin sondaj: este permisă

Regula generală la inventariere este stabilirea stocurilor faptice prin numărare, cântărire sau măsurare, bun cu bun. Normele legale prevăd însă și excepții explicite, în care verificarea prin sondaj este nu doar permisă, ci recomandată din motive practice — de exemplu, atunci când desfacerea integrală a ambalajelor ar fi ineficientă sau ar deteriora marfa.

## Temeiul legal

::: ghid-temei
„15. – (1) Stabilirea stocurilor faptice se face prin numărare, cântărire, măsurare sau cubare, după caz. Bunurile aflate în ambalaje originale intacte se desfac prin sondaj, acest lucru urmând a fi menționat și în listele de inventariere respective."
— OMFP nr. 2.861/2009, pct. 15 alin. (1) (sursă: anaf_surse/omfp_2861_2009.txt)
:::

Din normă rezultă condițiile stricte în care sondajul e admis:

- Sondajul se aplică **exclusiv bunurilor aflate în ambalaje originale intacte** — nu oricărui tip de stoc, și nu ca metodă generală de accelerare a inventarierii.
- Faptul că verificarea s-a făcut prin sondaj, și nu prin desfacerea fiecărui ambalaj, **trebuie menționat expres** în listele de inventariere — omiterea acestei mențiuni transformă o inventariere legitimă într-una neconformă din punct de vedere documentar.
- Normele mai permit, separat, ca materialele de masă (ciment, oțel beton, produse agricole etc.), a căror cântărire ar necesita cheltuieli importante sau ar degrada bunul, să fie inventariate pe bază de calcule tehnice — o altă excepție de la numărarea exhaustivă, cu mențiune obligatorie a modului de calcul în listă.

## Ce se greșește în practică

- Se extinde inventarierea prin sondaj la orice categorie de stoc, nu doar la bunurile în ambalaje originale intacte, considerând-o o metodă generală de eficientizare.
- Se omite mențiunea explicită din listele de inventariere despre faptul că verificarea s-a făcut prin sondaj — fără această notă, comisia de inventariere nu poate justifica ulterior metoda folosită.
- Se confundă inventarierea prin sondaj a bunurilor în ambalaje intacte cu verificarea prin sondaj a operațiunilor contabile sau a sistemului informatic, care este o cerință complet diferită, cu alt temei legal.

## Ce face iConta.eu

La data acestui ghid, iConta.eu oferă un modul de înregistrare a rezultatelor inventarierii — note de plus și de minus, pentru stocuri și mijloace fixe (`core/inventariere.py`) — pe baza cărora se generează notele contabile de regularizare. Aplicația **nu efectuează inventarierea faptică** și nu decide dacă un bun poate fi verificat prin sondaj; comisia de inventariere este cea care stabilește metoda de numărare la fața locului și consemnează în lista de inventariere modul de verificare folosit, iar iConta.eu preia doar rezultatul final.

[iConta.eu](/)
