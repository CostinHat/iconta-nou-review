---
title: "Cum verifici contul 421 cu statul de salarii?"
description: "Funcția contului 421 „Personal — salarii datorate” în planul de conturi general și logica de verificare a soldului lui față de statul de plată."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verifici contul 421 cu statul de salarii?

Contul 421 e „nodul" contabil prin care trece practic orice element al salarizării — de la datoria brută către angajat, până la rețineri și plata efectivă. Verificarea lui cu statul de plată nu înseamnă doar comparație de solduri, ci înțelegerea a ce anume ar trebui să reflecte fiecare rulaj.

## Temeiul legal

::: ghid-temei
„Din grupa 42 «Personal și conturi asimilate» fac parte: Contul 421 «Personal - salarii datorate» Cu ajutorul acestui cont se ține evidența decontărilor cu personalul pentru drepturile salariale cuvenite acestuia în bani sau în natură, inclusiv a sporurilor, adaosurilor, premiilor din fondul de salarii etc. Contul 421 «Personal - salarii datorate» este un cont de pasiv. [...] Soldul contului reprezintă drepturile salariale datorate."
— OMFP 1802/2014 pentru aprobarea Reglementărilor contabile privind situațiile financiare anuale individuale și situațiile financiare anuale consolidate, funcțiunea contului 421 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- În **credit**, contul 421 se alimentează cu „salariile și alte drepturi cuvenite personalului" (din contul 641 — cheltuieli cu salariile) și cu „contravaloarea avantajelor în natură acordate salariaților" (din 642) — deci creditul contului reflectă întreaga datorie brută a firmei față de angajați pentru luna respectivă.
- În **debit**, contul se descarcă prin: reținerile din salariu (avansuri, contribuții sociale reținute, impozit pe salarii — din conturile 425, 427, 431, 437, 428, 444), contravaloarea plăților în natură, drepturile de personal neridicate (transferate la 426) și, în final, salariile nete achitate efectiv (din 512 sau 531).
- **Soldul creditor** al contului 421, la finalul lunii, reprezintă exact „drepturile salariale datorate" — adică salariile nete rămase de plătit angajaților la acel moment, indiferent dacă au fost virate integral sau nu.
- Verificarea cu statul de plată constă, în esență, în confirmarea că salariul net calculat pentru fiecare angajat (brut, minus rețineri) corespunde cu ce a intrat, respectiv a ieșit, din contul 421 în luna respectivă — iar soldul rămas (dacă există) trebuie să corespundă salariilor neplătite efectiv până la data verificării.

## Ce se greșește în practică

- Se compară direct soldul contului 421 cu totalul brut al statului de plată, deși soldul reprezintă drepturile **nete** rămase de plătit, nu salariul brut integral.
- Se omit din verificare rulajele de debit reprezentând drepturi de personal neridicate (transferate la contul 426), ceea ce lasă un sold aparent nejustificat pe 421.
- Se confundă cheltuiala brută cu salariile (contul 641, cont de cheltuieli, care nu se închide niciodată pe același sold cu 421) cu obligația efectivă de plată către angajați — cele două conturi au funcții diferite și nu trebuie „să iasă" identic la orice verificare.
- Nu se reconciliază lunar reținerile din 421 (contribuții, impozit) cu sumele efectiv declarate și plătite la buget, ceea ce poate ascunde diferențe reale de calcul, nu doar de rotunjire.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează automat notele contabile lunare pentru statul de plată, folosind exact structura descrisă mai sus: contul 421 e creditat cu salariile brute și avantajele în natură, iar sumele fiscale reținute (impozit — 444, CAS — 4315, CASS — 4316) sunt preluate direct din declarația D112 a lunii respective, pentru ca nota contabilă să rămână sincronizată cu ce s-a declarat efectiv la ANAF. Aplicația nu forțează o comparație automată între soldul brut din statul de plată și baza contributivă din D112, pentru că acestea sunt, structural, mărimi diferite (baza contributivă exclude, de exemplu, facilitatea fiscală pentru salariul minim) — o eventuală divergență reală rămâne, deocamdată, o verificare manuală a contabilului.

[iConta.eu](/)
