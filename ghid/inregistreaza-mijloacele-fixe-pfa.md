---
title: "Cum se înregistrează mijloacele fixe la PFA?"
description: "Ce cere Codul fiscal pentru un PFA în sistem real la achiziția și amortizarea unui mijloc fix: respectarea regulilor de amortizare din Titlul II, evidențiate în Registrul-inventar."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează mijloacele fixe la PFA?

O persoană fizică autorizată (PFA) în sistem real nu ține contabilitate în partidă dublă, cu conturi de imobilizări și amortizare cumulată — ține evidență fiscală în **Registrul-inventar** și **Registrul de evidență fiscală**. Dar asta nu înseamnă că poate trece integral pe cheltuială costul unui mijloc fix în anul cumpărării: legea îi cere explicit să respecte aceleași reguli de amortizare ca o persoană juridică.

## Temeiul legal

::: ghid-temei
„(4) Condițiile generale pe care trebuie să le îndeplinească cheltuielile efectuate în scopul desfășurării activității independente, pentru a putea fi deduse, în funcție de natura acestora, sunt: [...] d) să respecte regulile privind amortizarea, prevăzute în titlul II, după caz."
— Codul fiscal, art. 68 alin. (4) lit. d) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„(7) Nu sunt cheltuieli deductibile: [...] h) cheltuielile de achiziționare sau de fabricare a bunurilor și a drepturilor amortizabile din Registrul-inventar; [...] k^1) cheltuielile cu amortizarea bunurilor din patrimoniul personal afectate exercitării activității, potrivit legii."
— Codul fiscal, art. 68 alin. (7) lit. h) și lit. k^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă practic pentru un PFA în sistem real:

- **Costul de achiziție al unui bun amortizabil nu e deductibil direct**, integral, în anul cumpărării — se recuperează prin **amortizare**, conform acelorași reguli de la Titlul II Cod fiscal aplicabile persoanelor juridice (definiția mijlocului fix, pragul valoric, metodele de amortizare — liniară, degresivă, accelerată — și duratele normale de utilizare).
- Bunul se înscrie în **Registrul-inventar**, nu într-un cont de imobilizări (214/213 etc.) — evidența e specifică sistemului în partidă simplă.
- Chiar și bunurile din patrimoniul personal, dacă sunt afectate activității, se amortizează după aceleași reguli, nu se trec direct pe cheltuială.
- Pragul valoric de încadrare ca mijloc fix (art. 28 alin. 2 lit. b Cod fiscal, 5.000 lei de la 25.02.2026) și regimurile speciale de amortizare (de exemplu amortizarea superaccelerată temporară pentru 2026, art. 28 alin. 8^1) se aplică identic, indiferent dacă cumpărătorul e persoană juridică sau PFA în sistem real.

## Ce se greșește în practică

- Se trece integral costul unui echipament pe cheltuială deductibilă în anul achiziției, ca și cum ar fi un consumabil, ignorând obligația de amortizare impusă explicit de trimiterea la Titlul II.
- Se confundă PFA în sistem real (venit net determinat pe baza contabilității în partidă simplă, cu Registru-inventar și reguli de amortizare) cu PFA la normă de venit, unde nu se conduce evidență a cheltuielilor efective și deci nici amortizare în acest sens.
- Se aplică regulile de amortizare fără să se verifice pragul valoric și data de intrare în vigoare a acestuia — pragul s-a schimbat în cursul lui 2026, iar bunurile intrate anterior schimbării urmează regula tranzitorie, nu pragul curent.

## Ce face iConta.eu

Funcționalitatea **Import mijloace fixe (migrare)** din iConta.eu (`core/mijloace_fixe_import_api.py`) și registrul de mijloace fixe curent (`core/repo_mijloace_fixe.py`, cu nota lunară de amortizare 6811 = cont amortizare) sunt construite pentru firme care țin **contabilitate în partidă dublă** — lucrează cu conturi de imobilizări (21x), amortizare cumulată (28x) și note contabile în notația 371/401 etc. **Nu se aplică unui PFA în sistem real**, care nu ține aceste conturi.

Verificat direct în cod: aplicația recunoaște explicit categoria „partidă simplă (PFA/II/PFL)" ca regim contabil distinct — de exemplu, aceste firme sunt excluse necondiționat din obligațiile D406 și D100/D101 (declarații specifice persoanelor juridice), iar impozitul pe venit al PFA se declară prin **Declarația unică (D212)**, nu prin declarațiile de profit. Dar iConta.eu **nu are, la data acestui ghid, un modul dedicat de evidență a mijloacelor fixe și amortizării în regimul specific PFA/Registrul-inventar** — funcționalitățile existente de mijloace fixe presupun partidă dublă. Pentru un PFA în sistem real, aplicarea corectă a regulilor de amortizare de mai sus (prag valoric, metodă, durată) rămâne, azi, o evidență ținută separat de contabil, în afara acestor module.

[iConta.eu](/)
