---
title: "Cheltuieli cu activele în construcție: deducerea la impozit"
description: "De ce cheltuielile capitalizate în imobilizări în curs de execuție nu sunt deductibile direct, ci abia prin amortizare, după punerea în funcțiune."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cheltuieli cu activele în construcție: deducerea la impozit

Un activ „în curs de execuție" (o clădire încă în construcție, un utilaj în montaj) nu generează deducere fiscală imediată pentru cheltuielile înglobate în el — pentru că, potrivit Codului fiscal, doar un mijloc fix efectiv utilizat se califică drept amortizabil.

## Temeiul legal

::: ghid-temei
„Mijlocul fix amortizabil este orice imobilizare corporală care îndeplinește cumulativ următoarele condiții: a) este deținut și utilizat în producția, livrarea de bunuri sau în prestarea de servicii, pentru a fi închiriat terților sau în scopuri administrative; b) la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei [...]; c) are o durată normală de utilizare mai mare de un an."
— Legea nr. 227/2015, art. 28 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Evaluarea imobilizărilor corporale și necorporale, cu ocazia inventarierii, se face la valoarea de inventar, stabilită de comisia de inventariere sau de evaluatori autorizați, potrivit legii. Fac obiectul evaluării și imobilizările în curs de execuție."
— OMFP nr. 1.802/2014, pct. 85 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Ce rezultă din cele două texte, combinate:

- Condiția de la art. 28 alin. (2) lit. a) — activul trebuie să fie „**deținut și utilizat**" — nu e îndeplinită cât timp construcția sau montajul nu sunt finalizate; o imobilizare în curs de execuție nu e, din punct de vedere fiscal, un mijloc fix amortizabil.
- Cheltuielile cu materialele, manopera, proiectarea etc. legate de activul în construcție **se capitalizează** în contul de imobilizări în curs (231/233, potrivit reglementărilor contabile), nu se trec direct pe cheltuieli deductibile ale exercițiului — indiferent cât timp durează execuția.
- Deducerea fiscală a acestor costuri se produce abia **după punerea în funcțiune**, prin amortizare, conform regulilor obișnuite ale art. 28 — durata normală de utilizare și metoda de amortizare se stabilesc atunci, nu în timpul execuției.
- Norma contabilă (OMFP 1802/2014) confirmă că imobilizările în curs de execuție rămân, totuși, obiect al inventarierii și evaluării anuale — ele există în contabilitate ca activ, chiar dacă nu generează încă deducere fiscală prin amortizare.

## Ce se greșește în practică

- Se deduc direct, ca cheltuieli ale exercițiului, costuri care de fapt reprezintă investiții în curs (de exemplu materiale de construcție consumate pentru un sediu în șantier) — corect e capitalizarea lor, urmată de amortizare după finalizare.
- Se amână greșit evaluarea/inventarierea imobilizărilor în curs, considerând că „nu sunt încă mijloace fixe" și deci nu intră în perimetrul inventarierii anuale — norma contabilă le include explicit.
- Se confundă momentul recepției fizice a lucrării (de exemplu recepția la terminarea construcției) cu momentul punerii în funcțiune relevant fiscal — cele două pot să nu coincidă, iar amortizarea fiscală pornește de la punerea efectivă în funcțiune.

## Ce face iConta.eu

Modulul de amortizare a mijloacelor fixe din iConta.eu (`core/d406_active.py`) calculează amortizarea fiscală începând de la data punerii în funcțiune a unui activ, în conformitate cu art. 28 — aplicația nu tratează costurile capitalizate în imobilizări în curs de execuție ca deductibile înainte de acel moment. Evidența separată a imobilizărilor în curs (conturile 231/233) și transferul lor la mijloace fixe finalizate rămân introduceri contabile pe care contabilul le face în aplicație, la momentul recepției/punerii în funcțiune.

[iConta.eu](/)
