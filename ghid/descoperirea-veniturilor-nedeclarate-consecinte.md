---
title: "Descoperirea veniturilor nedeclarate: consecințe"
description: "Ce se întâmplă fiscal și financiar când organul fiscal descoperă venituri nedeclarate: estimarea bazei de impozitare, dobânzi și penalitatea de nedeclarare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Descoperirea veniturilor nedeclarate: consecințe

Când organul fiscal constată, în cadrul unui control sau al unei verificări documentare, că un contribuabil a avut venituri nedeclarate sau declarate incorect, legea îi dă instrumentele să stabilească oricum baza de impozitare — chiar și fără o declarație corectă din partea contribuabilului — și să aplice sancțiuni fiscale specifice, separate de eventuala răspundere penală pentru evaziune.

## Temeiul legal

::: ghid-temei
„(1) Organul fiscal stabilește baza de impozitare și creanța fiscală aferentă, prin estimarea rezonabilă a bazei de impozitare, folosind orice probă și mijloc de probă prevăzute de lege, ori de câte ori acesta nu poate determina situația fiscală corectă. [...]
(1) Pentru obligațiile fiscale principale nedeclarate sau declarate incorect de contribuabil/plătitor și stabilite de organul fiscal prin decizii de impunere, contribuabilul/plătitorul datorează o penalitate de nedeclarare de 0,08% pe fiecare zi, începând cu ziua imediat următoare scadenței și până la data stingerii sumei datorate, inclusiv [...]
(3) Penalitatea de nedeclarare prevăzută la alin. (1) se majorează cu 100% în cazul în care obligațiile fiscale principale au rezultat ca urmare a săvârșirii unor fapte de evaziune fiscală, constatate de organele judiciare, potrivit legii."
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 106 alin. (1) și art. 181 alin. (1), (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Organul fiscal **nu are nevoie de o declarație corectă** ca să impună o obligație fiscală: dacă evidențele sunt incorecte, incomplete sau lipsesc, poate estima rezonabil baza de impozitare pe orice probă admisă de lege (art. 106 alin. (2) lit. b)).
- Pe lângă impozitul/contribuția stabilite suplimentar și dobânzile de întârziere obișnuite, se datorează separat **penalitatea de nedeclarare de 0,08%/zi**, calculată din ziua următoare scadenței inițiale — deci retroactiv, nu de la data controlului.
- Dacă faptele sunt calificate de organele judiciare drept **evaziune fiscală**, penalitatea de nedeclarare se dublează (majorare cu 100%).
- Penalitatea se reduce cu 75% dacă suma stabilită prin decizie este achitată sau eșalonată rapid (art. 181 alin. (2)), un stimulent real pentru a nu contesta la nesfârșit o sumă corect stabilită.
- Pentru persoane fizice, aceleași reguli de estimare se aplică și veniturilor a căror sursă nu a fost identificată în cadrul verificării situației fiscale personale (art. 181 alin. (12)).

## Ce se greșește în practică

- Se crede că, fără declarație depusă de contribuabil, organul fiscal „nu are de unde ști" suma datorată — de fapt, estimarea rezonabilă e un drept expres al organului fiscal (art. 106).
- Se ignoră faptul că penalitatea de nedeclarare (0,08%/zi) se cumulează cu dobânda de întârziere obișnuită, nu o înlocuiește (art. 181 alin. (4)).
- Se presupune că plata imediată a sumei stabilite prin decizie „anulează" penalitatea — de fapt doar o reduce cu 75%, dacă plata/eșalonarea se face în termenul legal.
- Se subestimează riscul calificării ca evaziune fiscală, care dublează penalitatea și deschide și răspunderea penală, separată de cea fiscală.

## Ce face iConta.eu

iConta.eu nu descoperă și nu raportează venituri nedeclarate — nu e rolul unei aplicații de contabilitate. Aplicația are însă un modul de **alerte de control fiscal** (`control_fiscal_api.py`, `alerte_control_fiscal.py`) care compară obligațiile declarative datorate cu cele efectiv depuse și semnalează firmei nepotrivirile (declarații lipsă, discrepanțe cu datele ANAF) înainte ca acestea să devină un motiv de inspecție. Scopul e prevenția — reducerea riscului de a ajunge exact în situația descrisă mai sus — nu constatarea propriu-zisă a veniturilor nedeclarate, care rămâne atribuția exclusivă a organului fiscal.

[iConta.eu](/)
