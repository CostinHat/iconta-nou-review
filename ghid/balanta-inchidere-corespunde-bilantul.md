---
title: Ce fac dacă balanța de închidere nu corespunde cu bilanțul?
description: Ce înseamnă avertismentul automat de discrepanță dintre activul net și capitalurile proprii la generarea S1005/S1003, și de unde vine de obicei diferența.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă balanța de închidere nu corespunde cu bilanțul?

Bilanțul respectă, prin construcție, principiul egalității: activul net (total activ minus datorii) trebuie să fie egal cu totalul capitalurilor proprii. Când cele două valori nu coincid, problema e aproape întotdeauna în balanța de verificare folosită la generare, nu în formularul în sine.

## Temeiul legal

::: ghid-temei
Persoanele prevăzute la art. 1 alin. (1)-(4) au obligația să întocmească situații financiare anuale.
— Legea contabilității nr. 82/1991, republicată, art. 28 alin. (1)
:::

Imaginea fidelă a poziției financiare presupune, la nivel elementar, coerența dintre activul net raportat și capitalurile proprii raportate — cele două trebuie să fie egale, ca o consecință directă a dublei înregistrări contabile. O discrepanță între ele nu e o eroare „de bilanț", ci semnul unei balanțe de verificare neechilibrate sau incomplete la data generării.

## Ce se greșește în practică

- Se generează bilanțul dintr-o balanță de verificare care conține înregistrări nevalidate sau incomplete pentru anul respectiv, iar diferența activ net / capitaluri proprii trece neobservată.
- Se ignoră avertismentul de discrepanță afișat la generare, presupunând că e o eroare „cosmetică" a formularului, nu un semnal real de neechilibru în balanță.

## Ce face iConta.eu

Verificarea este deja implementată, nu doar o temă de recomandare: la generarea S1005/S1003, `core/bilant_api.py` compară explicit rândul F(rd15) — activul net — cu rândul J(rd49) — total capitaluri proprii — și, dacă cele două nu coincid, adaugă un avertisment automat de tipul „Verificare: F(rd15)=... != J(rd49)=...". Acest avertisment apare **înainte** de generarea efectivă a XML-ului, tocmai pentru a semnala problema la sursă. Cauza cea mai frecventă este o balanță de verificare neechilibrată sau incompletă (înregistrări nevalidate încă, solduri inițiale introduse greșit) — corectarea se face în balanță, la conturile implicate, nu în bilanț.

[iConta.eu](/)
