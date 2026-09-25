---
title: "Un televizor cumpărat de firmă este mijloc fix?"
description: "Cele două condiții cumulative — durata de utilizare și valoarea minimă de 5.000 lei — care decid dacă un bun cumpărat de firmă e mijloc fix sau obiect de inventar."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Un televizor cumpărat de firmă este mijloc fix?

Depinde exclusiv de două criterii, aplicate cumulativ — nu de natura bunului în sine. Un televizor nu e „automat" mijloc fix sau „automat" obiect de inventar; devine una sau alta în funcție de durata pentru care e ținut în firmă și de valoarea lui de achiziție.

## Temeiul legal

::: ghid-temei
„mijloc fix - orice imobilizare corporală, care este deținută pentru a fi utilizată în producția sau livrarea de bunuri ori în prestarea de servicii, pentru a fi închiriată terților sau în scopuri administrative, dacă are o durată normală de utilizare mai mare de un an și o valoare egală sau mai mare decât limita stabilită prin hotărâre a Guvernului."
— Legea 227/2015 (Codul fiscal), art. 7 pct. 21 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei; această limită se actualizată anual, în funcție de indicele de inflație, prin hotărâre a Guvernului;"
— Legea 227/2015 (Codul fiscal), art. 28 alin. (2) lit. b), în forma modificată de OUG 8/2026 (în vigoare de la 25.02.2026; anterior, limita era 2.500 lei, stabilită prin HG 276/2013) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cele două condiții **cumulative**, aplicate unui televizor cumpărat de firmă:

- **Durata de utilizare**: trebuie să fie mai mare de un an. Dacă firma îl folosește ca bun de scurtă durată (de exemplu pentru un eveniment) și îl scoate din gestiune în câteva luni, condiția nu e îndeplinită, indiferent de preț.
- **Valoarea de achiziție**: trebuie să fie egală sau mai mare decât limita stabilită prin hotărâre de Guvern — **5.000 lei**, de la 25.02.2026 (OUG 8/2026), în locul pragului anterior de 2.500 lei (HG 276/2013).
- Dacă **ambele** condiții sunt îndeplinite (durată peste un an și preț de cel puțin 5.000 lei), televizorul se înregistrează ca mijloc fix, se amortizează pe durata normală de utilizare corespunzătoare categoriei lui din catalogul mijloacelor fixe.
- Dacă **oricare** dintre condiții lipsește — fie durata de utilizare planificată e sub un an, fie valoarea e sub 5.000 lei — bunul se înregistrează ca **obiect de inventar**, cu regim contabil diferit (de regulă, trecut integral pe cheltuieli la darea în folosință sau eșalonat pe perioada de utilizare, nu amortizat conform planului de amortizare al mijloacelor fixe).
- Pentru mijloacele fixe deja existente în patrimoniu la 31.12.2025, cu valoare între 2.500 și 5.000 lei, legea nu cere reclasificare ca obiecte de inventar — ele continuă să se amortizeze pe durata rămasă (art. 45 alin. (21^3) Cod fiscal).
- Scopul folosirii (activitate economică, uz administrativ) e și el relevant pentru calificarea drept mijloc fix, dar nu înlocuiește niciuna dintre cele două praguri de mai sus.

## Ce se greșește în practică

- Se stabilește regimul contabil al televizorului doar după valoare, ignorând complet condiția duratei de utilizare mai mare de un an.
- Se aplică pragul vechi (2.500 lei, valabil până la 24.02.2026) în loc de pragul actual de 5.000 lei, în vigoare de la 25.02.2026 prin OUG 8/2026.
- Se presupune că bunurile „electronice/electrocasnice" sunt automat obiecte de inventar, indiferent de preț — clasificarea corectă depinde strict de cele două praguri legale, nu de tipul bunului.

## Ce face iConta.eu

Verificat în cod: `core/obiecte_inventar.py` citește pragul valoric al mijlocului fix dintr-un registru de cote istoricizat (`prag_mf(la_data)`), nu dintr-o valoare fixă — pentru achizițiile de la 25.02.2026 încoace pragul aplicat este 5.000 lei (OUG 8/2026), iar pentru cele anterioare, 2.500 lei (HG 276/2013), fiecare corect legat de data operațiunii. Verificarea celeilalte condiții — durata reală de utilizare planificată de firmă pentru bunul respectiv — rămâne o evaluare a contabilului la momentul înregistrării achiziției.

[iConta.eu](/)
