---
title: Cum ține contabilitatea un PFA în sistem real?
description: În sistem real, venitul net se calculează pe baza contabilității (încasări și plăți efective, validate cu documente), ca diferență între venitul brut și cheltuielile deductibile care îndeplinesc condițiile legale.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum ține contabilitatea un PFA în sistem real?

Spre deosebire de norma de venit (unde impozitul se calculează pe o sumă fixă stabilită de ANAF), sistemul real cere ținerea efectivă a contabilității: fiecare încasare și fiecare cheltuială trebuie înregistrată și, pentru cheltuieli, justificată cu documente. Venitul net rezultă strict din diferența dintre ce a intrat și ce a ieșit, nu dintr-o estimare.

## Temeiul legal

::: ghid-temei
**Art. 68 alin.(1):** "Venitul net anual din activități independente se determină în sistem real, pe baza datelor din contabilitate, ca diferență între venitul brut și cheltuielile deductibile efectuate în scopul realizării de venituri, cu excepția situațiilor în care sunt aplicabile prevederile art. 68^1, 68^3 și 69."

**Art. 68 alin.(4):** condiții cumulative pentru deductibilitatea cheltuielilor: "să fie efectuate în cadrul activităților independente, justificate prin documente" (lit.a), "să fie cuprinse în cheltuielile exercițiului financiar al anului în cursul căruia au fost plătite" (lit.b) ș.a.m.d.

**Art. 68 alin.(5):** cheltuieli deductibile limitat — burse private (max 5% din baza de calcul), protocol (max 2%), cheltuieli sociale (max 5% din cheltuielile cu salariile) etc.
:::

## Trei categorii de operațiuni, tratate diferit

Contabilitatea unui PFA în sistem real, așa cum e organizată și în iConta.eu, separă operațiunile în trei categorii:

1. **Cheltuieli deductibile integral** — îndeplinesc toate condițiile de la art. 68 alin. (4): sunt legate de activitate, justificate prin documente, plătite în anul fiscal respectiv. Acestea scad direct venitul brut.
2. **Cheltuieli deductibile limitat** (art. 68 alin. (5)) — protocol, burse private, cheltuieli sociale ș.a., plafonate procentual. Partea care depășește plafonul nu e deductibilă.
3. **Operațiuni nevalidate (ciorne)** — introduse, dar neconfirmate cu document justificativ complet — nu intră în calculul venitului net până nu sunt validate.

## Ce se greșește în practică

- Se introduc cheltuieli fără document justificativ, în speranța că "se rezolvă mai târziu" — legal, condiția de justificare e obligatorie pentru deductibilitate.
- Se deduc integral cheltuieli de protocol sau cele cu caracter social, deși legea le plafonează procentual — depășirea plafonului rămâne nedeductibilă.
- Se contabilizează o cheltuială în anul facturării, nu în anul plății efective — în sistem real contează data plății, nu data facturii.
- Se lasă operațiuni "ciornă" nevalidate la sfârșit de an, iar acestea nu apar deloc în venitul net calculat, deși contribuabilul crede că au fost incluse.

## Ce face iConta.eu

Sursa cifrelor pentru D212 (`core/rip_api.py: fisa_d212`) însumează separat: încasările validate cu categoria "activitate" (venitul brut), plățile validate cu categoria "cheltuiala_deductibila" (cheltuielile deductibile integral) și raportează distinct cheltuielile din categoria "cheltuiala_limitata", cu un avertisment — pentru acestea, contabilul trebuie să stabilească manual partea deductibilă, conform plafoanelor de la art. 68 alin. (5). Operațiunile nevalidate (ciorne) nu intră în niciun calcul — sunt doar numărate, cu avertisment, pentru ca utilizatorul să știe că mai are operațiuni de confirmat înainte de a genera declarația finală.

[iConta.eu](/)
