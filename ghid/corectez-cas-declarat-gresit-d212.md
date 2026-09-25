---
title: "Cum corectez CAS declarat greșit în D212?"
description: "O contribuție de asigurări sociale declarată greșit în D212 se corectează prin rectificativă, cu baza de calcul recalculată corect pe treptele de 12/24 salarii minime brute."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez CAS declarat greșit în D212?

O eroare de CAS în D212 aproape întotdeauna vine dintr-o bază de calcul greșit stabilită — treapta de plafonare pe salarii minime brute e locul unde se strecoară cele mai multe greșeli. Corecția se face prin declarație rectificativă, cu baza recalculată corect.

## Temeiul legal

::: ghid-temei
„Baza anuală de calcul al contribuției de asigurări sociale, în cazul persoanelor care realizează veniturile prevăzute la art. 137 alin. (1) lit. b) și b^1), o reprezintă venitul ales de contribuabil, care nu poate fi mai mic decât: a) nivelul de 12 salarii minime brute pe țară, în cazul veniturilor realizate cuprinse între 12 salarii minime brute pe țară inclusiv și 24 de salarii minime brute pe țară; [...] b) nivelul de 24 de salarii minime brute pe țară, în cazul veniturilor realizate cel puțin egale cu 24 de salarii minime brute pe țară."
— Codul fiscal (Legea 227/2015), art. 148 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale."
— Legea 207/2015 (Codul de procedură fiscală), art. 105 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Pașii pentru o corecție reală, nu doar formală:

- Se recalculează venitul cumulat din toate sursele de activități independente și drepturi de proprietate intelectuală ale anului (art. 148 alin. (3)), pentru a stabili corect treapta de plafonare — 12 sau 24 de salarii minime brute.
- Baza de calcul e o valoare aleasă de contribuabil în interiorul treptei, nu venitul net efectiv — o eroare frecventă e declararea venitului net ca bază, în loc de una din cele două praguri.
- Se aplică cota de contribuție de la art. 138 lit. a) asupra bazei recalculate corect.
- Se depune declarația rectificativă (art. 105 alin. (1) și (3)), cu diferența de plătit sau de recuperat rezultată din recalculare.

## Ce se greșește în practică

- Se declară CAS pe venitul net efectiv, nu pe treapta de 12 sau 24 de salarii minime brute — baza de calcul e întotdeauna un multiplu al salariului minim, nu venitul propriu-zis.
- Se omite cumularea veniturilor din mai multe surse la stabilirea treptei de plafonare, declarând CAS separat pe fiecare sursă ca și cum ar fi independente.
- Se folosește salariul minim de la data depunerii declarației, nu cel de la 1 ianuarie a anului de realizare a venitului — plafoanele se raportează la reperul fix al începutului de an.

## Ce face iConta.eu

Motorul de calcul din `core/d212_engine.py` implementează exact regula de plafonare pe trepte pentru CAS (`calculeaza_cas`): sub pragul de 12 salarii minime brute contribuția e opțională, între 12 și 24 baza e fixă la 12 salarii minime, iar peste 24 baza e plafonată la 24 de salarii minime — cu reperul de salariu minim citit din registrul de cote al aplicației pentru anul de venit corect, nu hardcodat. Calculul e disponibil prin `fisa_d212` (`core/rip_api.py`) pentru contribuabilii cu evidență în Registrul-jurnal de încasări și plăți, dar numai pentru veniturile anilor 2025 și 2026.

Aplicația nu depune și nu generează automat declarația rectificativă — recalcularea corectă a bazei poate fi obținută din motorul de calcul, dar completarea și depunerea rectificativei D212 rămân manuale.

[iConta.eu](/)
