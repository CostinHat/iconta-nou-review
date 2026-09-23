---
title: Cum se taxează concediul medical pentru boală obișnuită?
description: Concediul medical e reglementat de OUG 158/2005, modificată prin Legea 141/2025 (de la 1 august 2025). Dosarul verificat pentru acest ghid nu detaliază mecanismul de taxare (CAS/CASS/impozit) al indemnizației — vezi ce e confirmat și ce nu.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se taxează concediul medical pentru boală obișnuită?

Indemnizația de concediu medical pentru boală obișnuică (incapacitate temporară de muncă) e reglementată de OUG 158/2005 privind concediile și indemnizațiile de asigurări sociale de sănătate, act modificat prin Legea 141/2025 — modificare aplicabilă de la 1 august 2025.

## Temeiul legal

::: ghid-temei
OUG nr. 158/2005 privind concediile și indemnizațiile de asigurări sociale de sănătate, cu modificările aduse de Legea 141/2025 (aplicabile de la 1 august 2025).
:::

**De semnalat onest**: dosarul de cercetare folosit la acest ghid acoperă în detaliu motorul de calcul al salariului obișnuit (`core/salarizare.py`, funcționalitatea F080 — CAS, CASS, impozit, deducere personală, facilități). Concediul medical a apărut doar incidental, în descrierea generală a funcționalității, cu mențiunea că Legea 141/2025 a schimbat procentele de calcul ale indemnizației (trei niveluri, 55/65/75%, în funcție de vechime/tip de incapacitate), fără ca sursa consultată să precizeze care procent corespunde exact bolii obișnuite și fără un citat verbatim din text. Din acest motiv, acest ghid nu afirmă un procent anume pentru boala obișnuită și nu detaliază regimul de CAS/CASS/impozit aplicabil indemnizației — o asemenea afirmație ar însemna o citare neconfirmată, ceea ce evităm explicit.

## Ce se greșește în practică

- Se presupune că indemnizația de concediu medical se calculează și se impozitează exact ca salariul obișnuit (aceleași cote, aceeași bază) — indemnizația de asigurări sociale de sănătate are un regim de calcul propriu (bază de calcul din venituri din ultimele luni, nu salariul lunii curente), diferit de motorul de calcul salarial obișnuit.
- Se ignoră faptul că, de la 1 august 2025, procentele de calcul ale indemnizației s-au schimbat prin Legea 141/2025 — o valoare veche, reținută din memorie, poate fi depășită.
- Se confundă baza de calcul a concediului medical cu brutul contractual al lunii în care începe concediul.

## Ce face iConta.eu

Motorul de calcul verificat pentru acest ghid (`core/salarizare.py`, funcția `calcul_salariu()` / `_calcul_salariu_2018()`) acoperă salariul obișnuit, plătit pentru timp efectiv lucrat — CAS 25%, CASS 10%, deducere personală, impozit 10%. Tratamentul specific al indemnizației de concediu medical (baza de calcul, procentele din OUG 158/2005 modificată, regimul de contribuții) nu face parte din codul verificat aici, ci dintr-o funcționalitate distinctă. Nu afirmăm, fără verificare directă a acelei funcționalități, cum anume calculează iConta.eu indemnizația de concediu medical — recomandăm verificarea directă în aplicație, la fluturașul de salariu al lunii respective.

[iConta.eu](/)
