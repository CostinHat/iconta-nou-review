---
title: "Cum se stabilește dacă o achiziție este mijloc fix sau obiect de inventar?"
description: "Pașii de verificare pe care legea îi cere înainte de a înregistra o achiziție ca mijloc fix sau ca obiect de inventar, și cum îi aplică automat iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se stabilește dacă o achiziție este mijloc fix sau obiect de inventar?

La fiecare achiziție de imobilizare corporală, contabilul trebuie să răspundă la o singură întrebare cu consecințe mari: se amortizează treptat (mijloc fix) sau se trece integral pe cheltuială (obiect de inventar)? Răspunsul nu e la alegere — rezultă din compararea valorii și duratei bunului cu pragurile din Codul fiscal, valabile la **data intrării în patrimoniu**.

## Temeiul legal

::: ghid-temei
„7. La articolul 28 alineatul (2), litera b) se modifică și va avea următorul cuprins: b) la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei; această limită se actualizată anual, în funcție de indicele de inflație, prin hotărâre a Guvernului;"
— OUG 8/2026, art. 6 pct. 7 (sursă: anaf_surse/oug_8_2026.html)
:::

Pașii pe care îi cere legea:

1. **Se stabilește data intrării în patrimoniu** — data facturii/documentului de achiziție, nu data plății sau a punerii în folosință.
2. **Se aplică pragul valabil la acea dată**: 5.000 lei pentru achiziții de la 25.02.2026 încolo, 2.500 lei pentru achizițiile anterioare.
3. **Se verifică și durata normală de utilizare** (Codul fiscal art. 28 alin. 2 lit. c) — dacă bunul are durată sub un an, e obiect de inventar indiferent de valoare, condiție separată de prag.
4. **Dacă bunul îndeplinește toate condițiile** (destinație + valoare ≥ prag + durată > 1 an), e mijloc fix și intră la amortizare. Altfel, e obiect de inventar: intră pe contul 303, iar la darea în folosință se trece integral pe cheltuială.

## Ce se greșește în practică

- Se compară valoarea cu pragul de la data facturii, dar se ia din memorie pragul vechi (2.500 lei) după 25.02.2026 — sau invers.
- Se generează nota de achiziție a obiectului de inventar fără cota de TVA declarată explicit, deși operațiunea o cere.
- Se ignoră condiția duratei sub un an și se forțează încadrarea ca mijloc fix doar pentru că valoarea depășește pragul.
- Se aplică pragul nou retroactiv unor bunuri deja existente la 31.12.2025 cu valoare între 2.500 și 5.000 lei — deși acestea rămân mijloace fixe, amortizate pe durata rămasă, fără reclasificare.

## Ce face iConta.eu

Din ecranul „Operațiuni speciale" → formularul „Obiecte de inventar (303)", iConta.eu verifică automat, înainte de a genera nota contabilă, dacă valoarea introdusă depășește pragul valabil la data operațiunii (citit dintr-un registru unic de cote, nu dintr-o constantă fixă în cod, tocmai ca să nu rămână desincronizat la o schimbare de prag). Dacă valoarea depășește pragul, aplicația respinge operațiunea „achiziție" cu un mesaj explicit care trimite la înregistrarea ca mijloc fix.

Pentru operația de achiziție, aplicația cere obligatoriu cota de TVA — o achiziție trimisă fără cotă e respinsă de server. Atenție însă: în formular, câmpul „Cota TVA %" e marcat vizual ca opțional pentru toate cele trei operații ale ecranului, deși pentru achiziție e de fapt obligatoriu; eroarea apare abia după trimitere, nu înainte. În ce privește criteriul de durată sub un an, motorul de calcul îl suportă și îl testează, dar formularul din interfață nu are încă un câmp pentru el — deci verificarea automată din acest ecran se bazează, pentru moment, exclusiv pe valoare.

[iConta.eu](/)
