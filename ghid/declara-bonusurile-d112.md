---
title: "Cum se declară bonusurile în D112?"
description: "Structura oficială a declarației D112 distinge între prima/bonusul ocazional și cel acordat prin contractul colectiv de muncă — două coduri diferite, cu tratament diferit."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se declară bonusurile în D112?

Un bonus plătit unui angajat nu e o categorie unică în declarația D112 — structura oficială a formularului distinge explicit între bonusul ocazional și cel prevăzut prin contractul colectiv de muncă, iar alegerea codului greșit poate distorsiona raportarea, chiar dacă suma și impozitarea sunt corecte.

## Temeiul legal

::: ghid-temei
„20.Prima/Bonus de natura ocazionala [...] 40.Prima/Bonus prev.prin Contract Colectiv de Munca"
— Structura declarației D112, nomenclatorul elementelor de venit (sursă: anaf_surse/d112_struct_anaf.txt)
:::

Ce trebuie reținut din structura oficială:

- **Codul 20** se folosește pentru prime/bonusuri **ocazionale** — sume acordate punctual, fără o obligație contractuală recurentă (de exemplu, un bonus de performanță acordat discreționar).
- **Codul 40** se folosește pentru prime/bonusuri prevăzute explicit prin **contractul colectiv de muncă** — sume la care angajatul are dreptul contractual, de regulă cu o regularitate sau condiții prestabilite.
- Ambele coduri intră, din punct de vedere fiscal, în categoria veniturilor asimilate salariilor, supuse acelorași contribuții și impozit pe venit ca salariul de bază — diferența dintre cele două coduri e de clasificare/raportare, nu de regim fiscal al sumei.
- Alegerea codului corect contează pentru coerența datelor raportate la ANAF și, indirect, pentru orice analiză ulterioară (control, reconciliere) care distinge tipurile de venituri salariale.

## Ce se greșește în practică

- Se raportează orice bonus la codul 20 (ocazional), indiferent dacă provine dintr-o obligație a contractului colectiv de muncă — ceea ce nu schimbă suma impozitului, dar denaturează structura reală a raportării.
- Se confundă bonusul cu alte elemente de venit similare (prime de vacanță, tichete de masă) care au coduri proprii separate în structura D112 — fiecare tip de beneficiu are propriul cod, nu se grupează sub "bonus" generic.
- Se omite verificarea contractului colectiv de muncă înainte de a decide codul — decizia corectă depinde de existența și conținutul acestui document, nu de denumirea internă dată bonusului în firma respectivă.

## Ce face iConta.eu

iConta.eu generează declarația D112 din statul de plată, calculând contribuțiile și impozitul pe baza sumelor introduse (salariu de bază, sporuri, bonusuri) — dar aplicația nu are, la acest moment, un câmp dedicat prin care contabilul să aleagă explicit între codul 20 (bonus ocazional) și codul 40 (bonus prin contract colectiv de muncă) din nomenclatorul oficial de elemente de venit. O sumă introdusă ca bonus e tratată, în stat, ca venit asimilat salariului, cu impozitarea corectă — clasificarea ei pe unul din cele două coduri ale nomenclatorului rămâne, pentru moment, în afara fluxului automatizat.

[iConta.eu](/)
