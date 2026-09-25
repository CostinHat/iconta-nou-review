---
title: "Greșeala de a nu reține corect CASS și CAS"
description: "Cotele legale de CAS și CASS pentru salariați, și de ce o reținere greșită la stat trebuie recalculată retroactiv, nu doar corectată de la luna curentă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Greșeala de a nu reține corect CASS și CAS

CAS și CASS nu sunt procente aproximative — sunt cote fixe, stabilite prin lege, aplicate la baza de calcul a fiecărui salariat. O reținere greșită, chiar și cu un procent apropiat de cel corect, generează o diferență care trebuie recalculată pe toată perioada afectată, nu doar corectată de la luna în care a fost observată.

## Temeiul legal

::: ghid-temei
„Cotele de contribuții de asigurări sociale sunt următoarele: a) 25% datorată de către persoanele fizice care au calitatea de angajați sau pentru care există obligația plății contribuției de asigurări sociale, potrivit prezentei legi; [...]"
— Legea nr. 227/2015 (Codul fiscal), art. 138 lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Pe lângă CAS, legea stabilește separat cota de CASS:

- **CAS (contribuția de asigurări sociale): 25%**, datorată de salariat, reținută la sursă de angajator din venitul brut din salarii (art. 138 lit. a).
- **CASS (contribuția de asigurări sociale de sănătate): 10%**, la fel datorată de angajat și reținută la sursă (art. 156).
- Angajatorul mai datorează, suplimentar, **4% sau 8%** pentru condiții deosebite/speciale de muncă, dar acestea sunt în sarcina angajatorului, nu rețineri din salariul angajatului.
- Baza de calcul pentru CAS și CASS nu e întotdeauna identică cu brutul contabil — pe lunile cu concediu medical, baza de contribuții se recalculează separat, conform regulilor OUG nr. 158/2005 privind indemnizațiile de asigurări sociale de sănătate.

## Ce se greșește în practică

- Se reține un procent apropiat, dar nu exact 25%/10%, dintr-o rotunjire greșită sau dintr-o formulă copiată dintr-un an fiscal anterior, cu cote deja modificate.
- Se corectează reținerea greșită doar de la luna curentă înainte, fără recalcularea retroactivă a lunilor în care CAS/CASS au fost reținute incorect — diferența rămâne, de fapt, o obligație nedeclarată.
- Se ignoră baza de calcul recalculată pe lunile cu concediu medical, aplicând CAS/CASS direct pe brutul contabil, care nu coincide cu baza de contribuții din acele luni.

## Ce face iConta.eu

iConta.eu calculează CAS și CASS la cotele legale curente (25%, respectiv 10%) pentru fiecare salariat, la generarea statului de plată și a declarației D112. Modulul de verificare încrucișată compară apoi totalurile CAS/CASS declarate în D112 cu rulajele conturilor de contribuții din balanță (4315/4316), pentru a semnala o eventuală divergență între ce a fost reținut și ce a fost declarat — dar recalcularea retroactivă a unor luni anterioare cu reținere greșită rămâne o intervenție manuală a contabilului.

[iConta.eu](/)
