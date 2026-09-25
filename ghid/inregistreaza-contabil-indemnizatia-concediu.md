---
title: "Cum se înregistrează contabil indemnizația de concediu?"
description: "Indemnizația de concediu de odihnă se înregistrează exact ca salariul — 641/421 — pentru că, legal, e un drept salarial ca oricare altul. Ce face iConta.eu pentru asta."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează contabil indemnizația de concediu?

Indemnizația de concediu de odihnă nu are un tratament contabil separat — pentru că, legal, nu e un venit distinct. E o formă a drepturilor salariale cuvenite angajatului, plătită pentru perioada în care acesta se află în concediu în loc să lucreze. Contabil, se înregistrează exact ca restul salariului lunii.

## Temeiul legal

::: ghid-temei
„Pentru perioada concediului de odihnă salariatul beneficiază de o indemnizaţie de concediu care nu poate fi mai mica decât valoarea totală a drepturilor salariale cuvenite pentru perioada respectiva."
— Legea 53/2003 (Codul muncii), art. 145 alin. (1) (sursă: anaf_surse/legea_53_2003_codul_muncii.txt)

„Contul 641 «Cheltuieli cu salariile personalului» [...] ține evidența cheltuielilor cu salariile personalului. În debitul contului 641 [...] se înregistrează: valoarea salariilor și a altor drepturi cuvenite personalului (421) [...]."

„Contul 421 «Personal - salarii datorate» [...] ține evidența decontărilor cu personalul pentru drepturile salariale cuvenite acestuia în bani sau în natură [...]. Contul 421 [...] este un cont de pasiv."
— OMFP 1802/2014 (Reglementările contabile), pct. 641 și pct. 421 din planul de conturi general (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Din combinarea celor două surse rezultă înregistrarea:

- Fiind un „drept salarial cuvenit personalului", indemnizația de concediu de odihnă intră în cheltuiala **641 „Cheltuieli cu salariile personalului"**, cu contrapartidă în **421 „Personal – salarii datorate"** — exact ca salariul de bază, nu printr-un cont separat.
- Peste ea se aplică apoi aceleași rețineri ca la orice altă componentă salarială — CAS 25%, CASS 10%, impozit 10% pe venitul net — reflectate prin conturile de datorii sociale și fiscale obișnuite (4315, 4316, 444).
- Termenul legal de plată contează și în contabilitate: indemnizația trebuie plătită (deci și decontată din 421) **cu cel puțin 5 zile lucrătoare înainte de plecarea în concediu**, nu neapărat la data obișnuită de plată a salariului.

## Ce se greșește în practică

- Se înregistrează indemnizația de concediu printr-un cont separat de cheltuială, ca și cum ar fi un beneficiu distinct de salariu, nu o componentă a acestuia.
- Se scade indemnizația din salariul brut al lunii, în loc să fie adăugată la el, ca parte a drepturilor salariale ale lunii respective.
- Se plătește indemnizația abia odată cu salariul lunii, ignorând termenul legal de 5 zile lucrătoare înainte de concediu.

## Ce face iConta.eu

iConta.eu nu tratează indemnizația de concediu de odihnă ca pe o sumă separată de salariu — contabilul o include în venitul brut al lunii, la fel ca orice alt element salarial, iar motorul de calcul al salariului (`core/salarizare.py`, `calcul_salariu`) generează automat nota contabilă completă (641/421, 421/4315, 421/4316, 421/444) pentru întreaga sumă. Aplicația nu are astăzi un calcul dedicat al zilelor și al sumei indemnizației de concediu de odihnă pornind de la perioada de concediu programată — acel calcul (media zilnică a lunii de concediu × zile) rămâne, pentru moment, în sarcina contabilului, la introducerea brutului lunii.

[iConta.eu](/)
