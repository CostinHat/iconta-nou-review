---
title: "Cum emit o factură cu taxare inversă în RO e-Factura?"
description: Obligația de bază e simplă — furnizorul nu înscrie TVA colectată și marchează factura cu mențiunea „taxare inversă"; beneficiarul autolichidează taxa. Detaliile tehnice exacte de marcare în fișierul RO e-Factura nu sunt acoperite de sursele verificate pentru acest ghid.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum emit o factură cu taxare inversă în RO e-Factura?

Indiferent de formatul facturii — pe hârtie, PDF sau transmisă prin sistemul RO e-Factura — regula de fond e aceeași: pentru operațiunile de la art. 331 din Codul fiscal, furnizorul nu înscrie taxa colectată pe factură, ci doar mențiunea „taxare inversă"; beneficiarul e cel care calculează și evidențiază taxa, atât ca taxă colectată, cât și ca taxă deductibilă.

## Temeiul legal

::: ghid-temei
„Pe facturile emise pentru livrările de bunuri/prestările de servicii prevăzute la alin. (2) furnizorii/prestatorii nu vor înscrie taxa colectată aferentă. Beneficiarii vor determina taxa aferentă, care se va evidenția în decontul prevăzut la art. 323, atât ca taxă colectată, cât și ca taxă deductibilă."
— Legea 227/2015, art. 331 alin. (3)
:::

::: ghid-temei
„Furnizorul/Prestatorul are obligația să înscrie pe factură mențiunea „taxare inversă"."
— HG 1/2016, pct. 109 alin. (1)
:::

Condiția de fond, verificată înainte de a emite factura: operațiunea trebuie să se regăsească la art. 331 alin. (2) CF (de exemplu deșeuri, cereale, clădiri/terenuri taxabile), ambele părți trebuie să fie înregistrate în scopuri de TVA, iar pentru categoriile cu termen (majoritatea, până la 31.12.2026) și cu prag valoric (telefoane, circuite integrate, console/tablete/laptopuri — de la 22.500 lei), aceste condiții trebuie și ele îndeplinite. Dacă oricare din condiții lipsește, nu se aplică taxare inversă, iar factura se emite cu TVA normal.

**Notă importantă**: sursele verificate pentru acest ghid confirmă obligația legală de mențiune și mecanismul contabil (`4426=4427` la beneficiar), precum și modul în care flagul de taxare inversă de pe factură alimentează automat declarațiile D300 și D394. Nu acoperă însă structura exactă a fișierului XML transmis prin sistemul RO e-Factura (câmpuri, coduri de scutire/simplificare specifice schemei) — pentru formatul tehnic exact al fișierului, verifică documentația tehnică oficială RO e-Factura, nu presupune un anumit câmp doar din regula de fond de mai sus.

## Ce se greșește în practică

- Se emite factura fără mențiunea explicită „taxare inversă", deși condițiile de fond sunt îndeplinite — norme pct. 109 alin. (4) prevede consecințe grave la beneficiar dacă mențiunea lipsește.
- Se aplică taxare inversă pe o categorie de bunuri/servicii care nu se regăsește la art. 331 alin. (2), doar pentru că partenerul e plătitor de TVA.
- Se ignoră termenul de expirare (31.12.2026, pentru majoritatea categoriilor) sau pragul de 22.500 lei (pentru telefoane, circuite integrate, console/tablete/laptopuri).

## Ce face iConta.eu

Odată ce marchezi o factură cu flagul de taxare inversă, aplicația o transmite automat cu tipul corespunzător în declarația D394 (tip „V" — livrare cu taxare inversă) și, pe latura de bază de impozitare, alimentează rândul 13 din D300. Ecranul dedicat categoriilor din art. 331 verifică, la nivel de notă contabilă (beneficiar), înregistrarea în scopuri de TVA a ambelor părți, expirarea și pragul valoric acolo unde se aplică. Structura tehnică exactă a fișierului XML transmis prin RO e-Factura nu a fost verificată separat pentru acest ghid — dacă întâmpini o eroare de validare la transmitere, verific-o direct în documentația tehnică RO e-Factura.

[iConta.eu](/)
