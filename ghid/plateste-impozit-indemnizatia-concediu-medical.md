---
title: "Se plătește impozit pentru indemnizația de concediu medical?"
description: "Regula impozitării indemnizației de concediu medical în 2026 — impozabilă pentru boala obișnuită, scutită pentru maternitate și îngrijirea copilului — și cum o aplică iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se plătește impozit pentru indemnizația de concediu medical?

Răspunsul depinde de motivul concediului. Pentru boala obișnuită, indemnizația e impozabilă, la fel ca salariul. Pentru alte situații — maternitate, îngrijirea copilului bolnav, risc maternal, îngrijirea unui pacient oncologic — Codul fiscal o scutește explicit de impozit.

## Temeiul legal

::: ghid-temei
„În înțelesul impozitului pe venit, următoarele venituri nu sunt impozabile: [...] b) indemnizațiile pentru incapacitate temporară de muncă acordate, potrivit legii, persoanelor fizice, altele decât cele care obțin venituri din salarii și asimilate salariilor; [...] c) indemnizațiile pentru: risc maternal, maternitate, creșterea copilului și îngrijirea copilului bolnav, îngrijirea pacientului cu afecțiuni oncologice, potrivit legii."
— Codul fiscal, art. 62 lit. b) și c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Interpretarea corectă a acestor litere, pentru un salariat:

- **Litera b) nu îl privește pe salariat** — scutirea se referă la indemnizația pentru incapacitate temporară de muncă primită de persoane care **nu** obțin venituri din salarii (de exemplu independenți asigurați facultativ). Pentru un angajat, indemnizația de boală obișnuită (cod 01) **este impozabilă**, ca orice venit asimilat salariului.
- **Litera c) e scutirea reală, aplicabilă salariaților**: indemnizațiile pentru **risc maternal, maternitate, creșterea/îngrijirea copilului bolnav și îngrijirea pacientului cu afecțiuni oncologice** nu se impozitează, indiferent că beneficiarul e salariat.
- Pentru celelalte coduri de indemnizație (boală obișnuită, carantină, reducere timp de muncă etc.), impozitul de 10% se aplică normal, pe baza rămasă după scăderea CAS și CASS.

## Ce se greșește în practică

- Se scutește de impozit orice concediu medical, pe motiv că „indemnizațiile pentru incapacitate temporară de muncă sunt neimpozabile" — scutirea de la litera b) nu se aplică salariaților.
- Se impozitează indemnizația de maternitate sau de îngrijire a copilului bolnav, ca și cum ar fi boală obișnuită.
- Se aplică scutirea și pentru carantină sau reducerea timpului de muncă, coduri care nu apar în lista de la litera c).

## Ce face iConta.eu

Motorul de calcul (`core/salarizare.py`, funcția `taxe_cm`) reține corect distincția din lege: aplică impozitul de 10% (pe baza rămasă după CAS și, unde e cazul, CASS) pentru boala obișnuită și celelalte coduri impozabile, dar **nu** reține niciun impozit pentru codurile de maternitate, îngrijire copil bolnav, risc maternal și îngrijire pacient oncologic — exact lista de la art. 62 lit. c). Calculul rulează automat la introducerea certificatului de concediu medical în fișa salariatului, cu rezultatul salvat odată cu certificatul.

[iConta.eu](/)
