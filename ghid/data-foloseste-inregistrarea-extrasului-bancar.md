---
title: "Ce dată se folosește la înregistrarea extrasului bancar?"
description: "Ce reglementează Ordinul 2634/2015 despre extrasul de cont ca document justificativ și principiul cronologic al înregistrărilor contabile."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce dată se folosește la înregistrarea extrasului bancar?

Extrasul de cont bancar este documentul care confirmă mișcările din contul firmei și, pentru multe operațiuni fără factură, este el însuși documentul justificativ pe baza căruia se face înregistrarea în contabilitate. Întrebarea care dată se folosește — data extrasului, data operațiunii sau data primirii lui de la bancă — se rezolvă din principiile generale ale Normelor privind documentele financiar-contabile, nu dintr-un articol dedicat exclusiv extrasului bancar.

## Temeiul legal

::: ghid-temei
„21. Înregistrările în contabilitate se fac cronologic, prin respectarea succesiunii documentelor după data de întocmire sau de intrare a acestora în entitate și sistematic, în conturi sintetice și analitice, în conformitate cu regulile stabilite pentru fiecare formă de înregistrare în contabilitate. [...]
25. Factura este document justificativ care stă la baza înregistrării în contabilitate a operațiunilor economice. Pentru operațiunile economice pentru care, conform prevederilor Codului fiscal, nu există obligația întocmirii facturii, înregistrarea în contabilitate a acestora se efectuează pe baza contractelor încheiate între părți și a documentelor financiar-contabile sau bancare care să ateste acele operațiuni, cum sunt: aviz de însoțire a mărfii, chitanță, dispoziție de plată/încasare, extras de cont bancar, notă de contabilitate etc., după caz."
— OMFP nr. 2634/2015, Anexa 1 (Norme generale), pct. 21 și pct. 25 (sursă: anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt)
:::

Din aceste două puncte rezultă regula practică: extrasul de cont este el însuși documentul justificativ (pct. 25), iar înregistrarea în contabilitate urmează succesiunea cronologică a documentelor „după data de întocmire sau de intrare a acestora în entitate" (pct. 21) — adică data la care extrasul respectiv a fost emis de bancă pentru perioada/ziua în cauză, nu data la care contabilul îl prelucrează efectiv.

## Ce se greșește în practică

- Se înregistrează operațiunile bancare la data la care contabilul a descărcat sau a primit extrasul (uneori cu zile sau săptămâni întârziere), în loc de data operațiunii așa cum reiese din extras.
- Se ignoră că extrasul de cont este suficient ca document justificativ de sine stătător pentru operațiunile fără factură (viramente, comisioane bancare, dobânzi), fără a mai fi nevoie de un document suplimentar.
- Se rup cronologia înregistrărilor atunci când extrasele sunt introduse în contabilitate în altă ordine decât cea a datelor lor, contrar principiului de la pct. 21.

## Ce face iConta.eu

iConta.eu importă extrasele de cont bancar (prin parsare automată sau introducere manuală) și le folosește ca sursă pentru înregistrările din jurnalul de bancă, păstrând data operațiunii așa cum apare în extras. Norma nu detaliază explicit un caz separat pentru „data extrasului" versus „data operațiunii" în sine — principiul cronologic general de mai sus este cel aplicat.

[iConta.eu](/)
