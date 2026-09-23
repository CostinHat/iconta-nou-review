---
title: Cum aleg perioada fiscală TVA pentru o firmă nouă?
description: Pentru o firmă nou-înregistrată TVA, periodicitatea depinde de cifra de afaceri estimată pentru restul anului — nu de o alegere liberă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum aleg perioada fiscală TVA pentru o firmă nouă?

Legea nu-ți lasă complet la liberă alegere lunar sau trimestrial — pentru o firmă nouă, decizia se bazează pe o estimare a cifrei de afaceri pentru perioada rămasă din an, declarată chiar la momentul înregistrării TVA.

## Temeiul legal

::: ghid-temei
**Art. 322 alin. (1) CF**: „Perioada fiscală este luna calendaristică." (regula generală)

**Art. 322 alin. (3) CF**: „Persoana impozabilă care se înregistrează în cursul anului trebuie să declare, cu ocazia înregistrării conform art. 316, cifra de afaceri pe care preconizează să o realizeze în perioada rămasă până la sfârșitul anului calendaristic. Dacă cifra de afaceri estimată nu depășește plafonul prevăzut la alin. (2), recalculat corespunzător numărului de luni rămase până la sfârșitul anului calendaristic, persoana impozabilă va depune deconturi trimestriale în anul înregistrării."

**Art. 322 alin. (2) CF** (plafonul de referință): „[...] plafonul de 100.000 euro [...], cu excepția situației în care persoana impozabilă a efectuat în cursul anului calendaristic precedent una sau mai multe achiziții intracomunitare de bunuri."

Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, liniile 21798-21819.
:::

La momentul înregistrării TVA (art. 316), firma trebuie să declare estimativ ce cifră de afaceri va realiza în lunile rămase până la finalul anului calendaristic. Dacă acea estimare, recalculată proporțional cu numărul de luni rămase, nu depășește plafonul de 100.000 euro, firma poate depune deconturi trimestriale chiar din anul înregistrării — nu trebuie să aștepte un an complet de activitate.

Excepția care anulează opțiunea trimestrială: dacă firma a efectuat deja (înainte de înregistrarea TVA) achiziții intracomunitare de bunuri în cursul anului respectiv, periodicitatea rămâne lunară, indiferent de cifra de afaceri estimată.

La finalul anului de înregistrare, dacă cifra de afaceri efectiv realizată (recalculată la an întreg) depășește plafonul, anul următor firma trece obligatoriu la decont lunar; dacă nu-l depășește, continuă trimestrial — tot cu excepția achizițiilor intracomunitare.

## Ce se greșește în practică

- Se presupune că o firmă nou-înregistrată TVA e automat pe decont lunar în primul an, fără să se verifice opțiunea trimestrială disponibilă prin estimarea de la art. 322 alin. (3).
- Se estimează cifra de afaceri pentru un an calendaristic întreg, nu pentru perioada rămasă efectiv până la sfârșitul anului, ceea ce duce la o comparație greșită cu plafonul recalculat.
- Se ignoră excepția achizițiilor intracomunitare — o firmă cu cifră de afaceri estimată mică, dar cu achiziții IC deja efectuate, nu poate opta pentru trimestrial.

## Ce face iConta.eu

La crearea unei firme, câmpul `tip_decont` (periodicitatea TVA) **nu se precompletează automat** — rămâne, conform deciziei de produs documentate în cod, „alegerea contabilului" (ANAF v9 nu întoarce această informație). Textul de ajutor din ecranul „Date firmă" parafrazează corect regula generală (lunar, cu excepția trimestrial dacă cifra de afaceri anul precedent e sub 100.000 euro și fără achiziții intracomunitare), dar aplicația nu calculează automat estimarea specifică firmelor nou-înregistrate din art. 322 alin. (3) — introducerea periodicității corecte, la firma nouă, rămâne un calcul manual al contabilului.

[iConta.eu](/)
