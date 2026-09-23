---
title: Raportarea sumelor în numărare la bilanț
description: Cum ajunge soldul de casă în rândul disponibilităților din bilanțul prescurtat (F10) și ce conturi contribuie efectiv la această valoare.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Raportarea sumelor în numărare la bilanț

Soldul de casă la 31 decembrie nu apare separat, pe un rând propriu, în bilanțul depus — el se cumulează cu celelalte disponibilități bănești ale firmei, într-un singur rând.

## Temeiul legal

::: ghid-temei
Persoanele prevăzute la art. 1 alin. (1)-(4) au obligația să întocmească situații financiare anuale.
— Legea contabilității nr. 82/1991, republicată, art. 28 alin. (1)
:::

Legea stabilește obligația de întocmire a bilanțului, dar conținutul tehnic exact al fiecărui rând al formularului S1005/S1003 (ce conturi intră unde) este stabilit prin ordin al ministrului finanțelor publice. Temeiul indicat inițial pentru acest formular, OMF 107/2025, a fost **abrogat integral** prin art. 13 din Ordinul nr. 2.036/23.12.2025 (Monitorul Oficial nr. 41/20.01.2026); textul actului succesor nu se regăsește în sursele verificate, așa că nu îl putem cita aici — ce putem confirma este comportamentul efectiv din motorul de generare, validat pe formatul XSD acceptat de ANAF.

## Ce se greșește în practică

- Se caută soldul de casă separat, pe un rând dedicat „numerar/casă", în bilanțul prescurtat — un asemenea rând distinct nu există; numerarul e inclus, cumulat, în rândul general al disponibilităților.
- Se lasă solduri creditoare sau necorelate pe conturile de trezorerie (531/532) nesoluționate înainte de generarea bilanțului, ceea ce distorsionează rândul de disponibilități.

## Ce face iConta.eu

Motorul de generare a bilanțului (`core/bilant.py`, funcția `f10_din_balanta`) calculează rândul de disponibilități al F10 ca sumă a soldurilor debitoare de pe conturile **5112, 512, 531, 532, 541, 542** — adică, pe lângă conturile bancare (512), acreditive și avansuri de trezorerie (541/542), sunt incluse explicit conturile de **casă în lei și în valută (531/532)**. Comportamentul e acoperit și de testul automat al aplicației (`test_bilant.py::test_f10_activ_simplu`), care confirmă că un sold pe contul „5311" contribuie la acest rând. Nu există, la acest moment, un rând separat pentru numerar în formularul prescurtat.

[iConta.eu](/)
