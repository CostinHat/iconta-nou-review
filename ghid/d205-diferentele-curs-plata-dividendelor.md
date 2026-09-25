---
title: "D205 și diferențele de curs la plata dividendelor"
description: "De ce D205 nu are legătură cu cursul valutar la dividende și care e, de fapt, regula care contează: cota de impozit în vigoare la data distribuirii."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# D205 și diferențele de curs la plata dividendelor

Titlul ăsta pornește dintr-o confuzie de nume: dividendele plătite unei persoane juridice sau fizice române nu au „diferențe de curs valutar" în sensul contabil (665/765), pentru că se distribuie și se plătesc în lei. Ce contează efectiv la plata dividendelor, și apare corect în D205, e cota de impozit reținută la sursă — care s-a schimbat în timp, de la 10% la 16%.

## Temeiul legal

::: ghid-temei
„Impozitul pe dividende se stabilește prin aplicarea unei cote de impozit de 16% asupra dividendului brut plătit unei persoane juridice române. [...]
[Art. 97 alin. (7)] Veniturile sub formă de dividende, inclusiv câștigul obținut ca urmare a deținerii de titluri de participare definite de legislația în materie la organisme de plasament colectiv, se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. [...]
[Art. VII] În cazul dividendelor distribuite în baza situațiilor financiare interimare întocmite în cursul anului 2025/anului fiscal modificat care începe în anul 2025, cota de impozit pe dividende este de 10%, fără recalcularea impozitului pe dividendele respective, după regularizarea acestora pe baza situațiilor financiare anuale [...]"
— Legea 141/2025, art. II pct. 1 (modifică art. 43 alin. (2) Cod fiscal), art. II pct. 5 (modifică art. 97 alin. (7) Cod fiscal) și art. VII (sursă: anaf_surse/legea_141_2025_consolidat.txt)
:::

- De la 1 ianuarie 2026, cota standard de impozit pe dividende, atât pentru persoane juridice cât și pentru persoane fizice, e **16%** (majorată de la 8%, prin Legea 141/2025).
- Pentru dividendele distribuite pe baza situațiilor financiare interimare din 2025, cota rămâne **10%**, chiar dacă plata efectivă are loc mai târziu, iar regularizarea pe situațiile financiare anuale nu recalculează impozitul deja reținut.
- Cota corectă se determină, deci, în funcție de **data la care s-a aprobat distribuirea** (interimară 2025 vs. distribuire ulterioară datei de 1 ianuarie 2026), nu în funcție de data plății efective.
- D205 (declarația informativă privind impozitul reținut la sursă) raportează exact această reținere, pe fiecare beneficiar și pe cota aplicabilă la momentul distribuirii respective.

## Ce se greșește în practică

- Se aplică o singură cotă tuturor dividendelor plătite într-un an, deși distribuiri aprobate în perioade diferite (2025 interimar vs. 2026) pot avea cote diferite pentru aceeași firmă.
- Se caută o legătură între „curs valutar" și D205, pornind de la denumiri interne de fișiere sau module care conțin cuvântul „curs" — dar care, verificat, se referă la succesiunea cronologică a distribuirilor, nu la rata de schimb BNR.
- Se omite reținerea distinctă pe fiecare distribuire, atunci când o firmă a aprobat dividende atât pe bază de situații interimare 2025, cât și pe bază de situații anuale ulterioare.

## Ce face iConta.eu

`core/d205.py` importă un modul numit `core/dividende_curs.py` — numele poate induce în eroare, dar acest modul **nu are nicio legătură cu cursul valutar BNR**. „Curs" se referă aici la succesiunea cronologică (FIFO pe dată) a distribuirilor și plăților de dividende, folosită pentru a aplica cota de impozit corectă în timp (10% pentru distribuiri pe bază de situații interimare 2025, 16% ulterior), conform Legii 141/2025 art. VII. Funcționalitatea de diferențe de curs valutar propriu-zisă (F041, `core/diferente_curs.py`) nu e apelată nicăieri din `d205.py` și nu are nimic de-a face cu plata dividendelor — dividendele nu generează diferențe de curs, fiind distribuite și plătite în lei.

[iConta.eu](/)
