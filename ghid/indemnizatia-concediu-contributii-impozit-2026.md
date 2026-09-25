---
title: "Indemnizația de concediu: contribuții și impozit 2026"
description: "De ce indemnizația de concediu de odihnă e taxată exact ca salariul (CAS, CASS, impozit) și cum o calculează iConta.eu prin același motor de salarizare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Indemnizația de concediu: contribuții și impozit 2026

Indemnizația de concediu de odihnă nu e un venit separat, cu regim fiscal propriu — e, din punct de vedere fiscal, salariu. Codul muncii îi garantează salariatului cel puțin drepturile salariale obișnuite pe perioada concediului, iar Codul fiscal o include explicit în categoria veniturilor din salarii, indiferent cum e ea denumită în statul de plată.

## Temeiul legal

::: ghid-temei
„Pentru perioada concediului de odihnă salariatul beneficiază de o indemnizaţie de concediu care nu poate fi mai mica decât valoarea totală a drepturilor salariale cuvenite pentru perioada respectiva."

„Sunt considerate venituri din salarii toate veniturile în bani și/sau în natură obținute de o persoană fizică rezidentă ori nerezidentă ce desfășoară o activitate în baza unui contract individual de muncă [...] indiferent de perioada la care se referă, de denumirea veniturilor ori de forma sub care ele se acordă [...]."
— Legea 53/2003 (Codul muncii), art. 145 alin. (1) (sursă: anaf_surse/legea_53_2003_codul_muncii.txt); Codul fiscal, art. 76 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Consecința practică:

- Indemnizația de concediu de odihnă se calculează ca **medie zilnică a veniturilor din luna/lunile în care e efectuat concediul, înmulțită cu numărul de zile de concediu** (Codul muncii, art. 145 alin. (2)).
- Fiind încadrată la venituri din salarii, i se aplică **exact aceleași rețineri ca salariului**: CAS 25%, CASS 10%, apoi impozit 10% pe venitul net rămas, cu deducerea personală, dacă e cazul.
- Nu există niciun regim de scutire sau cotă redusă pentru indemnizația de concediu de odihnă — spre deosebire de unele coduri de indemnizație de concediu medical, care sunt neimpozabile prin dispoziție expresă (art. 62 din Codul fiscal).
- Legea impune și un termen de plată: indemnizația se plătește **cu cel puțin 5 zile lucrătoare înainte de plecarea în concediu** (art. 145 alin. (3)).

## Ce se greșește în practică

- Se tratează indemnizația de concediu ca o sumă separată de salariu, cu propriile rețineri calculate distinct, în loc să fie inclusă în același calcul brut-net al lunii.
- Se confundă regimul fiscal al indemnizației de concediu de odihnă cu cel al concediului medical, care are coduri scutite de impozit sau de CASS prin lege — indemnizația de odihnă nu beneficiază de nicio asemenea scutire.
- Se plătește indemnizația împreună cu salariul lunii următoare, fără să se respecte termenul legal de 5 zile lucrătoare înainte de concediu.

## Ce face iConta.eu

iConta.eu nu are un calcul separat pentru „indemnizația de concediu de odihnă" — pentru că, fiscal, ea nu e un venit distinct. Contabilul introduce suma indemnizației (calculată conform art. 145, ca medie zilnică × zile) ca parte din venitul brut al lunii, iar restul îl face motorul de calcul al salariului (`core/salarizare.py`, `calcul_salariu`): CAS 25%, CASS 10%, impozit 10% pe net, exact ca la orice altă componentă a salariului, cu nota contabilă generată automat (641/421, 421/4315, 421/4316, 421/444). Aplicația nu calculează însă automat suma indemnizației pornind de la zilele de concediu programate — acel calcul (media zilnică din luna efectuării concediului × zile) rămâne în sarcina contabilului, la introducerea brutului lunii.

[iConta.eu](/)
