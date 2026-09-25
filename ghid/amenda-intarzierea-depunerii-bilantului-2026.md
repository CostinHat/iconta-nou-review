---
title: "Amenda pentru întârzierea depunerii bilanțului 2026"
description: "Sancțiunea contravențională pentru nedepunerea situațiilor financiare anuale la termen, potrivit Legii contabilității nr. 82/1991: amendă de la 2.000 la 5.000 lei."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Amenda pentru întârzierea depunerii bilanțului 2026

Depunerea cu întârziere sau nedepunerea situațiilor financiare anuale nu este doar o abatere administrativă „tolerată" — Legea contabilității o clasifică explicit drept contravenție, cu o amendă proprie, separată de alte sancțiuni fiscale.

## Temeiul legal

::: ghid-temei
„... 8. nedepunerea, potrivit prezentei legi, a situațiilor financiare anuale, a situațiilor financiare anuale consolidate, a situațiilor financiare interimare, precum și a raportărilor contabile;
[...]
ART. 42 (1) Contravențiile prevăzute la art. 41 se sancționează cu amendă după cum urmează: [...]
o) cea prevăzută la pct. 8, cu amendă de la 2.000 lei la 5.000 lei."
— Legea nr. 82/1991 (Legea contabilității), art. 41 pct. 8 și art. 42 alin. (1) lit. o) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Ce rezultă din text pentru bilanțul aferent anului 2026:

- Nedepunerea situațiilor financiare anuale este contravenție de sine stătătoare, cu **amendă între 2.000 și 5.000 lei**, indiferent de firmă.
- Legea sancționează separat și alte abateri conexe — de exemplu, prezentarea de situații financiare cu date eronate sau necorelate (pct. 3, amendă 1.000-3.000 lei) ori nerespectarea obligației membrilor organelor de conducere de a întocmi și publica situațiile financiare (pct. 5, amendă 1.000-5.000 lei) — deci întârzierea propriu-zisă și alte tipuri de neconformitate au regimuri de amendă distincte.
- Guvernul poate modifica nivelul amenzilor în funcție de rata inflației (art. 42 alin. (3)), deci valorile citate rămân cele din forma consolidată disponibilă și trebuie verificate la data faptei față de eventuale actualizări ulterioare.

## Ce se greșește în practică

- Se presupune că o depunere cu câteva zile întârziere „nu se sancționează în practică" — contravenția este definită de simpla nedepunere la termenul legal, indiferent de durata întârzierii.
- Se confundă amenda pentru nedepunere (pct. 8, art. 42 lit. o)) cu amenda pentru situații financiare cu date eronate (pct. 3, art. 42 lit. i)) — sunt fapte și cuantumuri diferite, deși ambele privesc situațiile financiare.
- Se ignoră termenele speciale pentru entitățile cu exercițiu financiar diferit de anul calendaristic (150, respectiv 120 de zile calendaristice de la închiderea exercițiului, potrivit art. 36 din aceeași lege), aplicând implicit termenul standard.

## Ce face iConta.eu

Verificat în cod: `core/bilant.py` generează situațiile financiare anuale ale microentităților (F10 bilanț prescurtat, F20 cont prescurtat, conform OMF 107/2025) din soldurile și rulajele balanței; aplicația nu are, la acest moment, o alertă automată de apropiere a termenului legal de depunere a situațiilor financiare care să prevină întârzierea — generarea la timp a bilanțului rămâne o responsabilitate a contabilului, cu sprijinul modulului de generare din aplicație.

[iConta.eu](/)
