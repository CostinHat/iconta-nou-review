---
title: "Cum corectez contabil o indemnizație de concediu neefectuat?"
description: "Compensarea în bani a concediului de odihnă neefectuat e permisă doar la încetarea contractului de muncă, se taxează ca salariul și se corectează prin regulile obișnuite de rectificare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez contabil o indemnizație de concediu neefectuat?

Compensarea în bani a zilelor de concediu de odihnă neefectuate nu e o opțiune oricând disponibilă — legea o permite strict într-un singur caz: încetarea contractului individual de muncă. O compensare acordată în afara acestui caz, sau calculată greșit, se corectează ca orice altă eroare de salarizare.

## Temeiul legal

::: ghid-temei
„Compensarea în bani a concediului de odihnă neefectuat este permisă numai în cazul încetării contractului individual de muncă."
— Legea 53/2003 (Codul muncii), art. 141 alin. (4) (sursă: anaf_surse/legea_53_2003_codul_muncii.txt)
:::

Ce înseamnă asta pentru corectarea unei înregistrări greșite:

- Dacă suma a fost acordată **în afara** unei încetări de contract (de exemplu, ca „bonus" pentru zile de concediu nefolosite, în timp ce salariatul rămâne angajat), înregistrarea e nelegală din start și trebuie stornată — legea nu permite compensare bănească decât la încetarea contractului.
- Dacă suma a fost calculată greșit (zile greșite, medie zilnică greșită), corectarea urmează regula generală de rectificare a înregistrărilor contabile și, dacă a fost deja declarată, a declarațiilor deja depuse.
- Fiind un drept salarial (nu un beneficiu separat), compensarea în bani se supune acelorași rețineri ca orice altă indemnizație de concediu: CAS, CASS, impozit pe venitul net.
- Corectarea afectează, de regulă, mai multe zone deodată: nota contabilă de salarii a lunii în care s-a acordat, declarația D112 aferentă și, dacă suma a fost deja plătită, decontul cu salariatul.

## Ce se greșește în practică

- Se acordă compensarea în bani unui salariat activ, pentru zile de concediu neefectuate, în loc să se programeze efectiv concediul rămas — situație nepermisă de lege.
- Se corectează doar suma din statul de plată, fără să se verifice dacă declarația D112 aferentă lunii respective a fost deja depusă și trebuie, la rândul ei, rectificată.
- Se tratează compensarea ca venit neimpozabil, pe motiv că „nu e salariu efectiv lucrat" — fiind drept salarial, se impozitează normal.

## Ce face iConta.eu

iConta.eu nu are o funcție dedicată pentru compensarea în bani a concediului de odihnă neefectuat — verificat în cod, nu există un calcul separat pentru acest caz, nici o validare care să blocheze introducerea unei asemenea sume în afara unei încetări de contract. Suma se introduce, ca orice alt element salarial, în venitul brut al lunii, iar motorul de calcul al salariului (`core/salarizare.py`) aplică restul reținerilor și generează nota contabilă obișnuită (641/421 etc.). Verificarea condiției legale (încetarea contractului) și corectitudinea calculului zilelor rămân în sarcina contabilului.

[iConta.eu](/)
