---
title: "Unde evidențiez pierderea fiscală reportată în D101?"
description: "Rândurile din declarația 101 unde se raportează pierderea fiscală curentă și cea recuperată din anii precedenți, potrivit instrucțiunilor ANAF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Unde evidențiez pierderea fiscală reportată în D101?

Pierderea fiscală nu dispare atunci când un exercițiu se închide pe minus — ea se reportează și se recuperează din profiturile viitoare, potrivit unor reguli precise. Declarația 101 are rânduri dedicate exact pentru urmărirea acestui report, distincte de rândul de profit/pierdere al anului curent.

## Temeiul legal

::: ghid-temei
„35 Total profit impozabil/pierdere fiscală pentru anul de raportare, înainte de ajustarea cu pierderile curente (rd. 22 + rd. 34)
36 Pierdere fiscală în perioada curentă, de reportat pentru perioada următoare
[...]
381 Profit impozabil/pierdere fiscală, înainte de reportarea pierderii din anii precedenţi (rd. 35 + rd. 36 + rd. 37 - rd. 38)
39 Pierdere fiscală de recuperat din anii precedenţi
391 Pierdere fiscală de recuperat în anul curent"
— Structura formularului 101, conform Ordinului președintelui A.N.A.F. nr. 206/2025 (sursă: anaf_surse/opanaf_206_2025_d101.txt)
:::

- **Rândul 35** arată profitul impozabil sau pierderea fiscală a anului de raportare, calculate **înainte** de ajustarea cu pierderile curente (rd. 22 + rd. 34) — practic rezultatul fiscal „brut" al perioadei curente.
- Dacă rezultatul de la rândul 35 e negativ, suma respectivă merge la **rândul 36** — pierderea fiscală curentă, cea care urmează să fie reportată pentru anii următori. Rândul **381** cumulează rd. 35+36+37-38 și arată rezultatul **înainte** de a aplica reportul din anii precedenți.
- **Rândul 39** conține stocul de pierdere fiscală acumulat din anii precedenți și încă nerecuperat, iar **rândul 391** izolează partea din acest stoc care se recuperează efectiv în anul curent.
- Legal, recuperarea se face în limita a 70% din profiturile impozabile viitoare, pe o perioadă de 5 ani consecutivi, în ordinea înregistrării pierderilor: „Pierderile fiscale anuale [...] se recuperează din profiturile impozabile realizate, în limita a 70% inclusiv, în următorii 5 ani consecutivi. Recuperarea pierderilor se va efectua în ordinea înregistrării acestora" (Legea nr. 227/2015, art. 31 alin. (1), sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt).

## Ce se greșește în practică

- Se completează direct rândul 39 cu pierderea din anul precedent fără să se verifice limita de 70% aplicabilă recuperării anuale — rândul 391 nu poate depăși acest plafon.
- Se amestecă pierderea fiscală curentă (rândul 36) cu cea recuperată din anii precedenți (rândurile 39/391), deși sunt fluxuri diferite ale aceluiași formular.
- Se pierde ordinea cronologică de recuperare — legea impune recuperarea „în ordinea înregistrării", nu la alegerea contribuabilului.
- În caz de fuziune/divizare, nu se aplică regula de proporționalitate cu activele transferate pentru preluarea pierderii fiscale de la societatea cedentă (art. 31 alin. (2)).

## Ce face iConta.eu

iConta.eu are un modul dedicat declarației 101 (`d101.py`), care preia automat din contabilitate baza de calcul a rezultatului (veniturile/cheltuielile de exploatare și financiare, rândurile P1/P2/P4/P5) și aplică formulele oficiale ale formularului pentru a obține profitul impozabil. Verificarea codului arată însă că rândurile **36, 39 și 391 (pierderea fiscală curentă și cea recuperată din anii precedenți) rămân intrări manuale ale contabilului**, cu valoare implicită 0 — aplicația nu ține un istoric multianual al pierderilor fiscale și nu le reportează automat de la un exercițiu la altul; chiar codul sursă documentează explicit că „ajustările fiscale (deduceri, nedeductibile, pierderi reportate...) sunt intrări manuale ale contabilului". Modulul `d101_reconciliere.py` recalculează independent doar baza contabilă (P1/P2/P4/P5) din balanță și o confruntă cu ce a generat `d101.py`, semnalând diferențe — el nu acoperă rândurile de pierdere fiscală (P6-P9 și cele de mai sus), care rămân, explicit, în afara acestei verificări.

[iConta.eu](/)
