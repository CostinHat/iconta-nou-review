---
title: Cum se înregistrează o încasare bancară de la client?
description: O încasare bancară de la un client se citește din extrasul de cont, se identifică partenerul după CUI din descriere și se leagă automat de facturile deschise ale acestuia — exact, prin combinații sau prin alocare parțială.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se înregistrează o încasare bancară de la client?

O încasare bancară de la un client se înregistrează pornind de la extrasul de cont — sistemul citește liniile extrasului, identifică partenerul din descriere și leagă suma încasată de facturile deschise ale acestuia, generând nota contabilă corespunzătoare (5121 = 4111).

## Temeiul legal

::: ghid-temei
"Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ." — Legea contabilității 82/1991, art. 6 alin. (1)

Extrasul de cont bancar e document justificativ expres pentru înregistrările în contabilitate, pentru operațiunile fără factură: "înregistrarea în contabilitate a acestora se efectuează pe baza contractelor... și a documentelor financiar-contabile sau bancare care să ateste acele operațiuni, cum sunt: aviz de însoțire a mărfii, chitanță, dispoziție de plată/încasare, **extras de cont bancar**, notă de contabilitate etc." — OMFP 2634/2015, Anexa 1, pct. 25
:::

Extrasul de cont e, alături de factură, documentul justificativ pe baza căruia se face înregistrarea contabilă a încasării. Disciplina de a verifica lunar corespondența dintre contabilitate și mișcările bancare are temei în obligația generală de întocmire a balanței de verificare — Legea 82/1991, art. 22.

## Ce se greșește în practică

Cea mai frecventă greșeală practică (verificată direct în comportamentul aplicației, nu doar teoretic): **reimportarea aceluiași extras bancar** (sau a unui extras cu interval de date suprapus) creează linii duplicate în sistem, fiecare putând fi alocată și contabilizată separat — risc real de dublă înregistrare a venitului și de dublă stingere a soldului unei facturi. A doua greșeală frecventă: amânarea reconcilierii lunare, care face ca eventuale erori de alocare să devină greu de corectat după închiderea perioadei contabile.

## Ce face iConta.eu

La importul extrasului de cont, aplicația citește fiecare linie și caută CUI-ul partenerului în descriere. Dacă găsește un CUI valid și acesta are facturi deschise (neîncasate) pe direcția de încasare, motorul de potrivire încearcă, în ordine: potrivire exactă cu o singură factură (verde), potrivire cu o combinație exactă de până la 4 facturi deschise ale aceluiași partener (verde), sau, dacă nu se potrivește exact, alocare FIFO pe facturile cele mai vechi, cu rest nealocat afișat (galben). Contabilizarea efectivă (butonul „Contează") generează nota 5121 = 4111 pentru fiecare alocare confirmată; dacă firma aplică TVA la încasare, se adaugă automat și linia de exigibilitate a TVA.

De reținut o limitare reală: aplicația **nu verifică duplicate la import** — reimportarea aceluiași fișier de extras produce linii noi, contabilizabile separat, fără avertisment automat. Pentru încasări cu cardul care vin în extras ca sumă cumulată pe mai mulți clienți (fără CUI unic) sau nete de comision, potrivirea automată nu funcționează ca la o încasare simplă cu CUI vizibil.

[iConta.eu](/)
