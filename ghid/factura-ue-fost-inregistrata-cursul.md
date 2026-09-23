---
title: "Ce fac dacă factura din UE a fost înregistrată la cursul valutar greșit?"
description: O achiziție intracomunitară înregistrată cu un curs valutar greșit se corectează prin stornarea integrală a notei greșite și înregistrarea unei note noi, cu cursul BNR corect de la data exigibilității taxei — nu prin editarea directă a sumelor deja înregistrate.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce fac dacă factura din UE a fost înregistrată la cursul valutar greșit?

O factură primită de la un furnizor din UE, pentru o achiziție intracomunitară, se înregistrează la cursul de schimb valabil la data exigibilității taxei — nu neapărat cursul din ziua în care factura a ajuns fizic sau a fost introdusă în contabilitate. Dacă înregistrarea inițială a folosit un curs greșit, corectarea nu se face prin simpla editare a sumei în lei — ci prin stornare și reînregistrare la cursul corect.

## Temeiul legal

::: ghid-temei
„Dacă elementele folosite pentru stabilirea bazei de impozitare a unei operațiuni, alta decât importul de bunuri, se exprimă în valută, cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a României […] valabil la data la care intervine exigibilitatea taxei pentru operațiunea în cauză." — Codul fiscal, art. 290 alin. (2).
:::

## De ce contează exact cursul folosit

Pentru achizițiile intracomunitare, taxarea inversă (autolichidarea TVA) presupune atât o taxă colectată, cât și una deductibilă, calculate pe aceeași bază — un curs greșit distorsionează ambele sume, cu efect direct în decontul de TVA (D300) și, dacă e cazul, în declarația recapitulativă (D390). Corecția nu e doar o chestiune de evidență internă: afectează cifre deja declarate la ANAF.

## Cum se corectează

Corecția se face prin stornarea integrală a notei contabile greșite (sumele se întorc cu semn negativ, păstrând cursul greșit al operațiunii originale — o stornare nu recalculează cursul), urmată de înregistrarea unei note noi, cu suma corectă în valută convertită la cursul BNR valabil la data exigibilității taxei operațiunii. Dacă factura greșită a fost deja inclusă într-un decont de TVA depus, corecția afectează și acel decont — verificați dacă e nevoie de un decont rectificativ, în funcție de perioada în care a fost depus.

## Ce se greșește în practică

- Se editează direct suma în lei a facturii deja înregistrate, fără o notă de stornare — pierzându-se urma contabilă a corecției și, adesea, generând o balanță neconcordantă cu decontul deja depus.
- Se folosește, la reînregistrare, cursul BNR din ziua corecției, în loc de cursul valabil la data exigibilității taxei operațiunii originale — data relevantă rămâne cea a operațiunii, nu cea a corectării ei.
- Se omite verificarea impactului asupra decontului de TVA deja depus, tratând corecția doar ca pe o problemă de evidență contabilă internă.

## Ce face iConta.eu

Stornarea unei note în aplicație întoarce aceleași sume cu semn negativ, la cursul facturii originale — nu recalculează cursul la stornare, exact pentru a păstra corectitudinea corecției pe aceeași bază ca înregistrarea inițială. Reînregistrarea la cursul corect se face ca o operațiune nouă, cu cursul BNR cerut explicit pentru data respectivă prin motorul de curs (`core/curs_bnr.py`) — aplicația nu presupune tăcut un curs implicit dacă acesta nu e introdus sau nu poate fi determinat pentru data cerută.

[iConta.eu](/)
