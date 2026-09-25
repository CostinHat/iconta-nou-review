---
title: "Deducerea amortizării neînregistrate în anii anteriori"
description: "Dacă amortizarea fiscală omisă în anii anteriori poate fi recuperată în anul curent sau trebuie corectată prin declarații rectificative, în limita termenului de prescripție."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Deducerea amortizării neînregistrate în anii anteriori

Amortizarea fiscală omisă acum trei ani nu poate fi pur și simplu „adunată" la cea din anul curent și dedusă dintr-odată — ea aparține fiscal anului în care ar fi trebuit calculată, iar corectarea se face prin declarații rectificative pentru anii respectivi, nu prin anul în curs.

## Temeiul legal

::: ghid-temei
„Cheltuielile aferente achiziționării, producerii, construirii mijloacelor fixe amortizabile, precum și investițiile efectuate la acestea se recuperează din punct de vedere fiscal prin deducerea amortizării potrivit prevederilor prezentului articol."
— Legea nr. 227/2015 (Codul fiscal), art. 28 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„(1) Dreptul organului fiscal de a stabili creanțe fiscale se prescrie în termen de 5 ani, cu excepția cazului în care legea dispune altfel. (2) Termenul de prescripție a dreptului prevăzut la alin. (1) începe să curgă de la data de 1 iulie a anului următor celui pentru care se datorează obligația fiscală, dacă legea nu dispune altfel."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 110 alin. (1) și (2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Din coroborarea celor două texte rezultă limitele reale ale corecției:

- Amortizarea fiscală se calculează pe baza duratei normale de utilizare a mijlocului fix, lunar, începând cu luna următoare punerii în funcțiune — este o cheltuială **aferentă unei anumite perioade fiscale**, nu o sumă globală recuperabilă oricând.
- Dacă amortizarea nu a fost dedusă corect într-un an anterior, corecția se face prin **declarație rectificativă** pentru anul (anii) respectiv, nu prin includerea sumei restante în calculul anului curent.
- Corecția este posibilă doar în limita **termenului de prescripție de 5 ani**, calculat de la 1 iulie a anului următor celui pentru care se datora obligația — dincolo de acest termen, dreptul de a mai regla fiscal acea perioadă se stinge.

## Ce se greșește în practică

- Se adaugă amortizarea omisă din anii trecuți la cheltuiala cu amortizarea din anul curent, distorsionând atât rezultatul fiscal al anului curent, cât și pe cel al anilor pentru care amortizarea era, de fapt, datorată.
- Se renunță la corectarea unei amortizări omise considerând că „nu mai merită", fără să se verifice dacă anul respectiv se mai află încă în termenul de prescripție de 5 ani.
- Se confundă eroarea de amortizare nedeclarată cu o simplă reevaluare a mijlocului fix — sunt operațiuni diferite, cu tratament și documentație distincte.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează amortizarea curentă a mijloacelor fixe, pe baza valorii de intrare, metodei și duratei normale de funcționare introduse (`core/d406_active.py`), dar **nu recalculează retroactiv** amortizarea omisă din anii anteriori și nu generează automat declarațiile rectificative aferente. Identificarea sumelor neînregistrate în trecut și corectarea lor, cu respectarea termenului de prescripție, rămân în sarcina contabilului.

[iConta.eu](/)
