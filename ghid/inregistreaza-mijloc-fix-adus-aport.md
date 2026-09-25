---
title: "Cum se înregistrează un mijloc fix adus ca aport la capitalul social?"
description: "Regulile de evaluare și înregistrare a unui bun adus ca aport în natură la capitalul social, conform Legii societăților și reglementărilor contabile."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează un mijloc fix adus ca aport la capitalul social?

Un asociat poate aduce, în locul unei sume de bani, un bun (un utilaj, un mijloc de transport, un echipament) ca aport la capitalul social. Legea admite acest tip de aport la toate formele de societate, dar îl condiționează de o evaluare economică, iar contabilitatea îi dă un regim de evaluare distinct de o achiziție obișnuită.

## Temeiul legal

```
::: ghid-temei
„(2) Aporturile în natură trebuie să fie evaluabile din punct de vedere economic. Ele sunt admise la toate formele de societate și sunt vărsate prin transferarea drepturilor corespunzătoare și prin predarea efectivă către societate a bunurilor aflate în stare de utilizare."
— Legea nr. 31/1990 a societăților, art. 16 alin. (2) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::
```

Iar din perspectiva evaluării contabile a bunului odată intrat în firmă:

```
::: ghid-temei
„La data intrării în entitate, bunurile se evaluează și se înregistrează în contabilitate la valoarea de intrare, care se stabilește astfel: [...] c) la valoarea de aport, stabilită în urma evaluării - pentru bunurile reprezentând aport la capitalul social [...]"
— OMFP nr. 1.802/2014 pentru aprobarea reglementărilor contabile privind situațiile financiare anuale individuale și consolidate, pct. 75 alin. (1) lit. c) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::
```

Ce rezultă, punând cele două texte cap la cap:

- **Bunul trebuie să fie evaluabil economic** — nu orice bun poate fi adus ca aport (de exemplu, prestațiile în muncă sau servicii sunt expres excluse de la art. 16 alin. (4) din Legea nr. 31/1990, indiferent de forma societății).
- **Se vărsă prin transferul efectiv al dreptului de proprietate și predarea bunului**, aflat în stare de utilizare — nu e suficientă doar mențiunea în actul constitutiv, trebuie să existe transferul real.
- **Dacă societatea se înființează de un asociat unic**, valoarea aportului în natură trebuie stabilită printr-o **expertiză de specialitate** (art. 13 alin. (3) din Legea nr. 31/1990) — o cerință suplimentară față de aportul cu mai mulți asociați, unde legea nu impune întotdeauna expertiză separată.
- **În contabilitate, mijlocul fix nu se înregistrează la costul lui istoric de achiziție de către asociat**, ci la **valoarea de aport, stabilită în urma evaluării** — practic valoarea din actul constitutiv/raportul de evaluare, nu prețul plătit inițial de asociat, care poate fi mai vechi sau diferit.

## Ce se greșește în practică

- Se înregistrează mijlocul fix la valoarea din factura de achiziție inițială a asociatului, în loc de valoarea de aport stabilită prin evaluare — cele două pot diferi semnificativ, mai ales dacă bunul e mai vechi.
- Se omite expertiza de evaluare la constituirea unei societăți cu asociat unic, deși legea o cere expres pentru acest caz.
- Se consideră aportul valabil doar pe baza mențiunii din actul constitutiv, fără predarea efectivă a bunului către societate — legea cere transferul real al dreptului și al posesiei.

## Ce face iConta.eu

Modulele de mijloace fixe din `core/` (`repo_mijloace_fixe.py`, `mijloace_fixe_import_api.py`, `inventariere.py`) gestionează evidența și amortizarea activelor odată introduse în contabilitate, la valoarea comunicată; introducerea specifică a unui bun la „valoarea de aport" stabilită prin evaluare, ca modalitate distinctă de intrare (față de achiziție sau producție proprie), rămâne o alegere pe care contabilul o face la înregistrarea inițială, aplicația nefiind identificată cu o rutină dedicată exclusiv acestui scenariu de intrare.

[iConta.eu](/)
