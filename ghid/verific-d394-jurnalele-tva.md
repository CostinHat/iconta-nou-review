---
title: "Cum verific D394 cu jurnalele de TVA?"
description: "Ce mecanisme de verificare există înainte de depunerea D394 și de ce nu există un jurnal de TVA separat de facturile din aplicație."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific D394 cu jurnalele de TVA?

Obligația de a ține evidențe corecte ale operațiunilor de TVA e generală, în Codul fiscal — dar forma concretă în care ții acele evidențe (jurnal separat, registru electronic, sau pur și simplu baza de date a facturilor) rămâne la latitudinea contribuabilului. Ce contează pentru D394 e ca cifrele declarate să corespundă cu operațiunile reale.

## Temeiul legal

::: ghid-temei
„Persoanele impozabile stabilite în România trebuie să țină evidențe corecte și complete ale tuturor operațiunilor efectuate în desfășurarea activității lor economice."
— Codul fiscal, art. 321 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt:21609-21612)
:::

Obligația de evidență corectă și completă e generală — legea nu impune un format anume de „jurnal de TVA", ci doar rezultatul: operațiunile trebuie să poată fi verificate și reconstituite.

## Ce se greșește în practică

- Se caută în aplicație un „jurnal de TVA" ca document separat de facturile emise și primite, deși evidența cerută de lege poate fi ținută direct din registrul de facturi, atât timp cât e corectă și completă.
- Se presupune că o declarație validată de validatorul oficial ANAF (DUK) e automat corectă și pe conținut — validarea DUK verifică structura XML-ului, nu dacă sumele corespund realității operațiunilor.
- Se ignoră faptul că D394 exclude anumite operațiuni (achizițiile intracomunitare, de exemplu) și apoi se caută, greșit, o discrepanță „nejustificată" între D394 și totalul facturilor de achiziție.

## Ce face iConta.eu

iConta.eu nu are un modul separat numit „jurnal de TVA" — D394 se generează direct din tabelele de facturi (`facturi` + `factura_linii`, `core/repo_d394.py`), aceleași folosite de restul aplicației, cu filtre explicite care exclud din generare documentele de tip proformă/aviz și facturile anulate sau stornate.

Înainte de a considera fișierul gata de depus, aplicația rulează două verificări:

1. **Validarea pe validatorul oficial ANAF (DUK)**, instalat local (`core/duk.py`), care confirmă că structura XML respectă schema oficială.
2. **O a doua cale de calcul, independentă** (`core/d394_reconciliere.py`), care recalculează totalurile pe fiecare cotă de TVA direct din liniile brute ale facturilor, cu cod separat de cel al generatorului principal, și **oprește generarea** dacă cele două calcule diferă.

Limitele acestor două gărzi sunt declarate explicit în cod: nu acoperă operațiunile manuale (bonuri fiscale, borderouri, care nu au ecran dedicat) și nu prind o eroare de intrare comună ambelor căi de calcul, cum ar fi o cotă de TVA tastată greșit o singură dată pe factură. Depunerea efectivă rămâne manuală, prin portalul SPV, cu fișierul deja validat.

[iConta.eu](/)
