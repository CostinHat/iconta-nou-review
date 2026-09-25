---
title: Cum corectez taxele unui administrator cu contract de mandat?
description: "Cele mai frecvente corecții: CAM aplicat greșit, temeiul legal citat greșit (lit. g în loc de lit. o) și amestecul cu regimul de salariat clasic."
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez taxele unui administrator cu contract de mandat?

Dacă indemnizația unui administrator cu contract de mandat a fost taxată greșit, cauza cea mai frecventă e citarea greșită a temeiului legal sau calculul greșit al bazei impozitului. Remunerația administratorului/directorului cu contract de mandat este venit asimilat salariilor și se datorează CAS 25%, CASS 10%, impozit 10% și CAM 2,25% (în sarcina societății) — CAM se datorează, potrivit art. 220^4 alin. (1) lit. d) și e) din Codul fiscal.

## Temeiul legal

::: ghid-temei
„remunerația administratorilor societăților, companiilor/societăților naționale și regiilor autonome, desemnați/numiți în condițiile legii, precum și sumele primite de reprezentanții în adunarea generală a acționarilor și în consiliul de administrație"

*(Codul fiscal — Legea nr. 227/2015, art. 76 alin. (2) lit. o))*
:::

## Cum verifici și corectezi

1. **Verifici dacă CAM a fost calculată.** Remunerația administratorului/directorului cu contract de mandat intră în baza CAM (art. 220^4 alin. (1) lit. d) și e) din Codul fiscal), deci CAM 2,25% se datorează — dacă a fost omisă, se adaugă și se corectează.
2. **Verifici baza de calcul a impozitului.** Impozitul de 10% se aplică pe (brut − CAS − CASS), în această ordine — nu pe brutul integral și nu doar pe brut minus CAS.
3. **Verifici temeiul legal citat în documentele interne.** Dacă a fost citat art. 76 alin. (2) lit. g) din Codul fiscal, e o citare greșită — lit. g) privește președintele asociației de proprietari, nu administratorul unei societăți. Temeiul corect e **lit. o)**.
4. **Recalculezi cu funcția de mandat** (CAS 25% + CASS 10% + impozit 10% pe rest, plus CAM 2,25% în sarcina societății) și refaci nota contabilă corectă, prin contul 621, nu 641.

## Ce se greșește în practică

- Omiterea CAM la indemnizația de mandat, presupunând greșit că nu se datorează — CAM se aplică remunerației administratorilor și directorilor cu contract de mandat.
- Citarea art. 76 alin. (2) lit. g) în locul lit. o) — o greșeală întâlnită și în documentația internă, nu doar în practica de birou.
- Recalcularea doar a impozitului, fără verificarea și a CAS/CASS, deși toate trei depind de aceeași bază brută.

## Ce face iConta.eu

Funcția `calcul_mandat(brut)` din modulul F021 (`core/contracte_speciale.py`) calculează întotdeauna CAS 25% + CASS 10% + impozit 10% pe rest, fără CAM — dacă o notă a fost introdusă anterior cu alt calcul (de exemplu prin fluxul de salarizare clasică), corectarea presupune stornarea acelei note și reintroducerea ei prin ecranul „Contracte speciale (zilieri, mandat, cenzori)", cu tipul „mandat". Aplicația nu recalculează automat notele deja introduse greșit prin alt flux.

[iConta.eu](/)
