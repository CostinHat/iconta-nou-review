---
title: De ce diferă impozitul pe salarii din D112 de balanța contabilă?
description: Impozitul pe salarii declarat în D112 (codul 602) trebuie să corespundă cu rulajul creditor al contului 444, cu o toleranță de rotunjire — orice diferență peste toleranță are o cauză identificabilă, nu întâmplătoare.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# De ce diferă impozitul pe salarii din D112 de balanța contabilă?

Impozitul pe venitul din salarii declarat în D112 și soldul contului 444 din balanță ar trebui să coincidă, cu o mică marjă de rotunjire. Când nu coincid, diferența are întotdeauna una din câteva cauze concrete — niciodată "așa e normal".

## Temeiul legal

::: ghid-temei
"Cota de impozit este de 10% și se aplică asupra venitului impozabil..." — Codul fiscal (Legea 227/2015), art. 64 alin. (1)
:::

D112 declară impozitul pe salarii sub codul de obligație **602**, iar în contabilitate el trebuie regăsit ca rulaj creditor al contului **444** (Impozitul pe venituri de natura salariilor). Cota aplicată e 10%, conform art. 64 alin. (1) din Codul fiscal.

Diferențele apar din câteva surse tipice, nu din întâmplare:

- **Rotunjire** — D112 rotunjește totalul la leu, contabilitatea nu; diferența crește cu numărul de salariați (până la aproximativ 0,5 lei per salariat), și de aceea verificarea folosește o toleranță proporțională, nu una fixă de 1 leu.
- **Stat de salarii necontabilizat** — dacă nota contabilă lipsește complet, contul 444 rămâne la zero în timp ce D112 declară o sumă.
- **Notă în ciornă** — nota există, dar nu a fost validată, deci nu intră în rulajul contabil folosit la comparație.
- **Corecții sau salariați adăugați/șterși ulterior** — modificări făcute în statul de plată după ce nota contabilă a fost deja înregistrată.
- **Sursă diferită a declarației** — dacă D112 a fost regenerată acum, dar la ANAF s-a depus o variantă anterioară (nepersistată), diferența poate reflecta o discrepanță între ce s-a depus efectiv și ce calculează acum aplicația.

## Ce se greșește în practică

Greșeala frecventă e presupunerea că diferența e "doar rotunjire" fără verificare — dincolo de toleranța calculată (0,5 lei/salariat, minim 1 leu), o diferență e reală și trebuie investigată. Altă greșeală e compararea impozitului cu brutul din contul 421, care nu e câmpul relevant — comparația corectă e cu contul 444.

## Ce face iConta.eu

Funcția `compara_d112` (`core/control_incrucisat.py`) compară exact suma declarată sub codul 602 cu rulajul creditor al contului 444, aplică toleranța corespunzătoare numărului de salariați și, dacă diferența depășește toleranța, indică remediul potrivit cauzei (contabilizare, validare notă sau investigație), niciodată o simplă marcare "diferență" fără explicație.

[iConta.eu](/)
