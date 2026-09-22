---
title: Cum declar în D212 trecerea de la normă de venit la sistem real?
description: Trecerea la sistem real se declară completând capitolul de sistem real din D212 cu venitul net calculat efectiv din contabilitate, iar dacă anul anterior a fost pe normă de venit, norma minimă legală rămâne de 12 salarii minime brute pe țară — dar calculul normei de venit nu e automatizat în aplicație.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum declar în D212 trecerea de la normă de venit la sistem real?

Trecerea de la normă de venit la sistem real înseamnă că, pentru anul de venit în care se face trecerea, PFA nu mai declară o sumă fixă stabilită de ANAF (norma de venit), ci calculează venitul net efectiv din contabilitate — venit brut minus cheltuieli deductibile. Declarația D212 pentru acel an se completează la capitolul de sistem real, nu la cel de normă de venit.

## Temeiul legal

::: ghid-temei
**Art. 69 alin.(3):** "Norma de venit pentru fiecare activitate desfășurată de contribuabil nu poate fi mai mică decât nivelul a 12 salarii de bază minime brute pe țară garantate în plată, în vigoare la data de 1 ianuarie a anului de realizare a venitului."

**Art. 68 alin.(1):** "Venitul net anual din activități independente se determină în sistem real, pe baza datelor din contabilitate, ca diferență între venitul brut și cheltuielile deductibile efectuate în scopul realizării de venituri, cu excepția situațiilor în care sunt aplicabile prevederile art. 68^1, 68^3 și 69."
:::

## Ce înseamnă practic trecerea

- Pentru **anul(ii) anterior(i)** în care PFA a fost pe normă de venit, venitul declarat rămâne cel calculat conform normei (minim 12 salarii minime brute pe țară pentru fiecare activitate, conform art. 69 alin. (3)) — acest calcul nu se schimbă retroactiv.
- Pentru **anul din care începe sistemul real**, contabilitatea trebuie ținută efectiv de la acea dată (încasări, plăți, documente justificative) — venitul net se determină ca diferență, nu ca normă.
- Capitolul din D212 pentru anul de tranziție e cel de **sistem real** (venit brut, cheltuieli deductibile, venit net), nu cel de normă de venit.

## Ce se greșește în practică

- Se completează în continuare capitolul de normă de venit din D212 pentru anul în care s-a trecut deja la sistem real.
- Se calculează greșit norma de venit pentru anii anteriori, ignorând pragul minim de 12 salarii minime brute pe țară per activitate.
- Se ține contabilitatea "informal", fără documente justificative complete, de la data trecerii — condiție obligatorie pentru ca cheltuielile să fie deductibile în sistem real.
- Se presupune că aplicația calculează automat norma de venit pentru anii anteriori, pentru comparație — motorul de calcul nu are această funcționalitate.

## Ce face iConta.eu

Motorul de calcul (`core/d212_engine.py`) calculează **exclusiv sistemul real** — nu conține nicio funcție pentru calculul normei de venit. Structura XML pentru capitolul de normă de venit (capitolul 12 din D212, câmpuri precum `real_norma_venit`, `real_venit_net_anual`) există în generatorul de declarație (`core/d212.py`), dar fără o funcție de calcul asociată în motor — dacă un an anterior a fost pe normă de venit, acele valori trebuie introduse manual, calculate separat conform art. 69. Pentru anul curent de tranziție la sistem real, aplicația completează automat capitolul de sistem real pe baza încasărilor și plăților validate din contabilitate.

[iConta.eu](/)
