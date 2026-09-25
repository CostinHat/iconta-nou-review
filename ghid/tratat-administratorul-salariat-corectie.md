---
title: "Am tratat administratorul ca salariat: corecție"
description: Cea mai completă formă a greșelii — CIM în loc de mandat, CAM reținut, D112 depus greșit. Ce se corectează și ce rămâne, inevitabil, un pas manual.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Am tratat administratorul ca salariat: corecție

Când un administrator cu contract de mandat e introdus în aplicație ca angajat obișnuit — pe fluxul de salarizare clasic, cu contract individual de muncă — greșeala nu e doar contabilă. Ea afectează contul folosit (641 în loc de 621) și, dacă declarația a fost deja depusă, tipul de asigurat raportat la stat — dar nu CAM: contribuția asiguratorie pentru muncă se datorează și pentru remunerația administratorului (art. 220^4 alin. (1) lit. d)), deci nu se stornează.

## Temeiul legal

::: ghid-temei
„remunerația administratorilor societăților, companiilor/societăților naționale și regiilor autonome, desemnați/numiți în condițiile legii, precum și sumele primite de reprezentanții în adunarea generală a acționarilor și în consiliul de administrație"

*(Codul fiscal — Legea nr. 227/2015, art. 76 alin. (2) lit. o))*
:::

## Ce corectezi, pas cu pas

1. **Scoți administratorul din fluxul de salarizare clasică** și îl reintroduci prin ecranul dedicat contractelor speciale, cu tipul „mandat".
2. **Nu stornezi CAM** — contribuția asiguratorie pentru muncă se datorează și pentru remunerația administratorului de mandat (art. 220^4 alin. (1) lit. d) din Codul fiscal include expres această remunerație în baza CAM).
3. **Muți cheltuiala din 641 în 621** — nu mai e cheltuială cu salariile din raport de muncă.
4. **Verifici dacă indemnizația a fost deja raportată în D112** ca angajat cu CIM (tip asigurat 1). Structura oficială D112 are o categorie distinctă pentru administratori — tip asigurat 6 — diferită de tip 1 (salariat clasic). Dacă declarația a fost deja depusă greșit, rectificarea ei e un pas separat, în afara notei contabile.

## Ce se greșește în practică

- Se oprește greșit CAM la corectare, deși CAM se datorează pentru remunerația administratorului; problema reală e că administratorul rămâne, structural, introdus ca „salariat" în sistemul de evidență a personalului.
- Se presupune că schimbarea tipului de contract în aplicație regenerează automat declarațiile deja depuse — nu e cazul, o declarație deja transmisă la ANAF se rectifică separat.
- Se ignoră diferența de temei legal (lit. o) pentru administrator, nu lit. g) sau regulile CIM), ceea ce poate duce la aplicarea altor plafoane sau exceptări nepotrivite.

## Ce face iConta.eu

Modulul F021 (`core/contracte_speciale.py`) oferă calculul corect (`calcul_mandat`) și nota corectă (`nota(fel="mandat")`, prin contul 621) pentru administratorul de mandat. O limitare de reținut, verificată direct în cod: generarea D112 din aplicație citește exclusiv din tabela de salariați cu contract individual de muncă (`asigCI="1" asigSO="1"`, hardcodat) — nu are, la acest moment, un traseu care să ducă o notă de mandat spre categoria corectă de „tip asigurat" (6, pentru administratori) din D112. Dacă administratorul a fost deja declarat greșit ca salariat cu CIM, rectificarea declarației rămâne un pas manual, în afara acestui modul.

[iConta.eu](/)
