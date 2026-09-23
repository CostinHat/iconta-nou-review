---
title: Cum se înregistrează contabil salariul administratorului?
description: Nota contabilă a indemnizației de mandat trece prin contul 621, nu 641 — distincția contează, pentru că administratorul cu mandat nu e salariat cu CIM.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se înregistrează contabil salariul administratorului?

Vorbim aici despre indemnizația unui administrator cu contract de mandat — nu de un administrator angajat suplimentar cu contract individual de muncă. Diferența contează pentru că, fiind o cheltuială cu personal din afara raportului de muncă, nu trece prin contul 641 (cheltuieli cu salariile personalului), ci prin 621 (cheltuieli cu colaboratorii).

## Temeiul legal

::: ghid-temei
„remunerația administratorilor societăților, companiilor/societăților naționale și regiilor autonome, desemnați/numiți în condițiile legii, precum și sumele primite de reprezentanții în adunarea generală a acționarilor și în consiliul de administrație"

*(Codul fiscal — Legea nr. 227/2015, art. 76 alin. (2) lit. o))*
:::

## Nota contabilă, pas cu pas

1. `621 = 421` — înregistrarea cheltuielii cu indemnizația brută a administratorului (nu `641`, pentru că nu e cheltuială cu salariile din raport de muncă).
2. `421 = 4315` — reținerea CAS (25% din brut).
3. `421 = 4316` — reținerea CASS (10% din brut), dacă suma rezultată e mai mare decât zero.
4. `421 = 444` — reținerea impozitului pe venit (10% din brut − CAS − CASS).
5. `421 = 5311` sau `421 = 5121` — plata efectivă a netului, în numerar sau prin bancă.

## Ce se greșește în practică

- **Indemnizația e trecută prin contul 641**, ca la un salariat clasic — corect e 621, pentru că mandatul de administrator nu e raport de muncă.
- **Se adaugă CAM** la cele trei rețineri de mai sus — CAM nu se datorează pentru administratorul cu mandat.
- **Nota e generată o singură dată pe an**, la fel ca la o remunerație ocazională — dacă indemnizația e lunară, fiecare lună are propria notă completă, cu propriile rețineri.

## Ce face iConta.eu

Funcția `nota(brut, fel="mandat", sursa, la_data)` din modulul F021 (`core/contracte_speciale.py`) generează exact secvența de mai sus: `621 → 421`, apoi `421 → 4315` (CAS), `421 → 4316` (CASS, doar dacă rezultă o sumă pozitivă), `421 → 444` (impozit), `421 → 5311/5121` (plata netului). Ecranul e disponibil în categoria „Personal și deconturi", sub „Contracte speciale (zilieri, mandat, cenzori)".

O limitare de reținut: nota generată de F021 nu are, în acest moment, o legătură funcțională cu generarea declarației D112 din aplicație — motorul D112 citește exclusiv din tabela de salariați cu contract individual de muncă, nu din notele de mandat/cenzor/zilier. Declararea la D112 (categoria „tip asigurat" 6, pentru administratori) rămâne, pentru moment, un pas separat de acest ecran.

[iConta.eu](/)
