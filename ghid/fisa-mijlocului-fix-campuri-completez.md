---
title: "Fișa mijlocului fix: ce câmpuri completez"
description: "Câmpurile pe care le urmărește iConta.eu pentru fiecare mijloc fix — cod, valoare, conturi, metodă, dată PIF, durată — și ce se întâmplă dacă unele lipsesc."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Fișa mijlocului fix: ce câmpuri completez

Pentru fiecare activ din registru, aplicația urmărește un set fix de câmpuri, atât la introducere manuală, cât și la import.

## Temeiul legal

::: ghid-temei
"Amortizarea fiscală se calculează după cum urmează: a) începând cu luna următoare celei în care mijlocul fix amortizabil se pune în funcțiune, prin aplicarea regimului de amortizare prevăzut la alin. (5);" — Codul fiscal, art. 28 alin. (12) lit. a)
:::

Câmpurile relevante fiscal sunt cele care alimentează motorul de amortizare: contul de imobilizare (determină categoria activului și, implicit, metodele permise), data de punere în funcțiune (de la care începe calculul), metoda de amortizare, valoarea de intrare, valoarea reziduală și durata normală de funcționare.

## Ce se greșește în practică

Se lasă necompletat contul de imobilizare ("categorie neclasificată"), ceea ce înseamnă că activul respectiv nu va putea folosi decât liniar/degresiv — orice metodă accelerată sau superaccelerată va fi refuzată la calcul până se completează contul.

## Ce face iConta.eu

La import (CSV/XLSX) sau introducere, câmpurile urmărite pentru un mijloc fix sunt: cod, denumire, cont de imobilizare, cont de amortizare, valoare, valoare reziduală și durata normală de funcționare (în luni). Aplicația blochează la import un cod lipsă sau duplicat, o durată ≤0, o valoare ≤0 sau un rezidual mai mare decât valoarea de intrare; pentru un cont de imobilizare lipsă, afișează doar un avertisment informativ, nu blocant.

[iConta.eu](/)
