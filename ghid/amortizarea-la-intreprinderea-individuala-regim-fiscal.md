---
title: Cum se amortizează mijloacele fixe la întreprinderea individuală?
description: Întreprinderea individuală (II) urmează exact același regim de amortizare ca PFA-ul — nu există un tratament distinct în sursele legale; ambele sunt "persoane care desfășoară activități independente" sub incidența acelorași articole din Codul fiscal.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se amortizează mijloacele fixe la întreprinderea individuală?

Există o presupunere frecventă că întreprinderea individuală (II) ar avea un regim fiscal special pentru amortizarea mijloacelor fixe, diferit de cel al unui PFA obișnuit. Nu este cazul: legea le tratează identic, ca formă de organizare a activității independente.

## Temeiul legal

::: ghid-temei
OMFP 170/2015, Cap. I, pct. 1: "persoanele fizice şi asocierile fără personalitate juridică, ale căror venituri sunt supuse impozitului pe venit ... al căror venit net anual este determinat în sistem real, pe baza datelor din contabilitate ... Persoanele care desfăşoară activități independente ... sunt persoanele care obțin venituri din: a.1 - activități economice (persoane fizice autorizate, întreprinderi individuale şi întreprinderi familiale) ..."

Codul fiscal, art. 28 alin. (2): "Mijlocul fix amortizabil este orice imobilizare corporală care îndeplinește cumulativ următoarele condiții: a) este deținut și utilizat în producția, livrarea de bunuri sau în prestarea de servicii, pentru a fi închiriat terților sau în scopuri administrative; b) la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei; ...; c) are o durată normală de utilizare mai mare de un an."

Codul fiscal, art. 28 alin. (6): "amortizarea se stabilește prin aplicarea cotei de amortizare liniară la valoarea fiscală de la data intrării în patrimoniul contribuabilului a mijlocului fix amortizabil."
:::

## Un singur regim, nu unul separat pentru II

OMFP 170/2015 tratează, explicit, "persoanele fizice autorizate, întreprinderile individuale și întreprinderile familiale" ca o singură categorie de contribuabili, supusă acelorași reguli de partidă simplă. Nu există, în textele legale verificate, un articol care să prevadă cote de amortizare, praguri sau durate normale de funcționare diferite pentru II față de PFA. Amortizarea unui mijloc fix cumpărat de o întreprindere individuală urmează exact aceleași reguli de la art. 28 din Codul fiscal — prag de 5.000 lei de la 25.02.2026, durată normală din Catalogul HG 2139/2004, metodă liniară (obligatorie pentru construcții, opțională pentru echipamente tehnologice și computere), start din luna următoare punerii în funcțiune.

Singurul element specific formei de organizare este identificarea contribuabilului (CUI-ul II în locul CNP-ului/CIF-ului PFA în documentele justificative) — nu regimul fiscal de amortizare în sine.

## Ce se greșește în practică

- Se caută (fără rezultat) un "regim special de amortizare pentru II", presupunând că forma juridică schimbă cotele sau duratele de amortizare — nu le schimbă.
- Se aplică din greșeală reguli de amortizare accelerată specifice altor tipuri de contribuabili (de exemplu societăți comerciale), deși II urmează regulile art. 28 comune tuturor persoanelor fizice care desfășoară activități independente.
- Se ține evidența mijloacelor fixe ale II separat, cu o metodologie diferită de cea a unui PFA, deși ambele completează aceeași Fișă a mijlocului fix (cod 14-2-2) și același Registru-inventar (cod 14-1-2/b).
- Se presupune că pragul valoric al mijlocului fix diferă pentru II — pragul (5.000 lei de la 25.02.2026) este unic, indiferent de forma de organizare.

## Ce face iConta.eu

Motorul de calcul din `core/rip_api.py` — inclusiv `registru_inventar(conn, schema, an)`, care calculează amortizarea liniară a mijloacelor fixe pe baza `dnf_luni`, `data_pif` și `valoare` din tabela `mijloace_fixe` — nu face nicio distincție de cod între PFA, întreprindere individuală sau întreprindere familială: toate rulează prin aceeași logică de validare, amortizare și calcul al Registrului-inventar, coerent cu faptul că sursele legale nu prevăd un regim distinct pentru II.

[iConta.eu](/)
