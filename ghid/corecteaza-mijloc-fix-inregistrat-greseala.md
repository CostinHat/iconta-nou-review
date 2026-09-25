---
title: "Cum se corectează un mijloc fix înregistrat din greșeală ca obiect de inventar?"
description: "Procedura de corectare a erorii contabile atunci când un bun care îndeplinea condițiile de mijloc fix a fost, din greșeală, trecut integral pe cheltuială ca obiect de inventar."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se corectează un mijloc fix înregistrat din greșeală ca obiect de inventar?

Dacă un bun care îndeplinea toate cele trei condiții din Codul fiscal (destinație, valoare peste prag, durată peste un an) a fost, din greșeală, trecut integral pe cheltuială ca obiect de inventar, în loc să intre la amortizare, eroarea trebuie corectată conform regulilor generale de corectare a erorilor contabile — nu printr-o simplă „mutare" de sold de pe un cont pe altul.

## Temeiul legal

::: ghid-temei
„65. - (1) Erorile constatate în contabilitate se pot referi fie la exercițiul financiar curent, fie la exercițiile financiare precedente. (2) Corectarea erorilor se efectuează la data constatării lor."
— OMFP 1802/2014, reglementări contabile, pct. 65 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.html)
:::

Ce impune procedura, în funcție de momentul descoperirii erorii:

- **Corectarea se face la data constatării erorii**, nu retroactiv la data achiziției — bunul nu se „rescrie" ca și cum ar fi fost dintotdeauna corect înregistrat.
- **Dacă eroarea aparține exercițiului financiar curent**, corectarea se efectuează pe seama contului de profit și pierdere: cheltuiala greșit înregistrată integral (603) se stornează, iar bunul se recunoaște corect ca imobilizare corporală, la valoarea lui de intrare, urmând să intre la amortizare de la data corectării.
- **Dacă eroarea aparține unui exercițiu financiar precedent și e semnificativă**, corectarea se face pe seama rezultatului reportat (contul 1174 „Rezultatul reportat provenit din corectarea erorilor contabile"), nu prin rescrierea situațiilor financiare deja depuse ale acelui exercițiu.
- **Stornarea operațiunii inițiale** se face fie cu semnul minus (stornare în roșu), fie prin înregistrarea inversă (stornare în negru), conform politicii contabile a firmei.
- Notele explicative la situațiile financiare trebuie să prezinte natura erorii constatate și perioada afectată de ea.

## Ce se greșește în practică

- Se face o simplă notă manuală de transfer între conturi, fără să se stornoze corect operațiunea inițială și fără documentarea erorii în notele explicative.
- Se corectează eroarea retroactiv, ca și cum bunul ar fi fost mijloc fix încă de la achiziție, fără să se respecte regula corectării la data constatării.
- Se ignoră pragul de semnificație — o eroare semnificativă dintr-un exercițiu precedent trebuie corectată pe rezultatul reportat, nu direct pe cheltuielile/veniturile perioadei curente.
- Se uită TVA-ul dedus greșit sau incomplet la achiziție, dacă tratamentul aplicat inițial (obiect de inventar vs. mijloc fix) a implicat o cotă sau o bază de calcul diferită.

## Ce face iConta.eu

Modulul de obiecte de inventar din iConta.eu (`core/obiecte_inventar.py`) acceptă exact trei operații: achiziție, dare în folosință și scoatere din uz. Aplicația **nu are** o funcție dedicată de reclasificare sau corectare care să treacă automat un bun deja înregistrat ca obiect de inventar în categoria mijloc fix. Corectarea unei asemenea erori — stornarea notei inițiale, recunoașterea bunului ca imobilizare corporală, pornirea amortizării — rămâne, azi, un proces manual, făcut de contabil prin notele contabile generale ale aplicației, nu printr-un ecran dedicat de corecție.

[iConta.eu](/)
