---
title: Cum se tratează fiscal produsele alimentare retrase din cauza temperaturii necorespunzătoare?
description: O defecțiune de temperatură nu e perisabilitate „de comercializare" în sensul HG 831/2004, ci degradare calitativă a stocului — deductibilă și scutită de ajustare TVA doar dacă distrugerea produselor e dovedită.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se tratează fiscal produsele alimentare retrase din cauza temperaturii necorespunzătoare?

O întrerupere a lanțului de frig sau o defecțiune de temperatură nu e o pierdere „firească" de comercializare, de tipul celor acoperite de coeficientul de perisabilitate din HG 831/2004 — e un caz de degradare calitativă a stocului, cu regim propriu, care depinde în întregime de dovada distrugerii efective a produselor retrase.

## Temeiul legal

::: ghid-temei
„Următoarele cheltuieli nu sunt deductibile: [...] c) cheltuielile privind bunurile de natura stocurilor sau a mijloacelor fixe amortizabile constatate lipsă din gestiune ori degradate, neimputabile, precum și taxa pe valoarea adăugată aferentă, dacă aceasta este datorată potrivit prevederilor titlului VII. Aceste cheltuieli sunt deductibile în următoarele situații/condiții: [...] 3. bunurile/mijloacele fixe amortizabile degradate calitativ, dacă se face dovada distrugerii; [...]"

*(Codul fiscal — Legea nr. 227/2015, art. 25 alin. (4) lit. c), teza introductivă și pct. 3)*
:::

## De ce nu e cazul clasic de perisabilitate

Titlul HG 831/2004 vizează explicit „mărfuri în procesul de comercializare" — manipulare și depozitare normală, cu pierderi firești încadrate într-un coeficient pe grupă. O defecțiune de temperatură (frigider/vitrină stricată, întrerupere de curent etc.) e un eveniment punctual de degradare calitativă, nu o pierdere firească repetabilă — motorul de perisabilitate al iConta nu are, oricum, coeficientul HG 831/2004 pentru a calcula o limită în acest caz, iar categoria legală relevantă e alta.

## Ce trebuie dovedit

Regula generală tratează bunurile constatate lipsă sau degradate, neimputabile, ca **nedeductibile**, cu TVA aferent datorat. Excepția care face cheltuiala deductibilă (și, prin trimitere la art. 304 alin. (2) lit. a), scutește de ajustarea TVA) cere ca degradarea calitativă să fie dovedită — practic, proces-verbal de constatare a defecțiunii (cu temperatura înregistrată, dacă e posibil) și dovada distrugerii efective a produselor (predare la eliminare, casare documentată).

## Ce se greșește în practică

- Se tratează retragerea produselor ca perisabilitate obișnuită și se aplică un coeficient HG 831/2004, deși evenimentul e o degradare calitativă punctuală, nu o pierdere firească de comercializare.
- Se scoate marfa din gestiune fără proces-verbal contemporan cu constatarea defecțiunii, ceea ce face imposibilă invocarea ulterioară a excepției.
- Se presupune deductibilitate automată doar pentru că temperatura a fost, evident, defectuoasă — fără dovada scrisă a distrugerii produselor.

## Ce face iConta.eu

Motorul F066 (`core/perisabilitati.py`) modelează exclusiv mecanismul de perisabilitate periodică din HG 831/2004 (coeficient pe grupă, aplicat la valoarea intrărilor) — nu are un flux dedicat pentru un eveniment punctual de degradare calitativă cauzat de o defecțiune tehnică. Pentru acest caz, aplicația nu calculează automat nimic; contabilul trebuie să evalueze direct, pe baza documentelor disponibile, dacă degradarea și distrugerea sunt dovedite corespunzător pentru a justifica deductibilitatea și scutirea de ajustare TVA.

[iConta.eu](/)
