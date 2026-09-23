---
title: "Cum corectez cursul valutar folosit la o factură în euro?"
description: Cursul valutar greșit de pe o factură deja înregistrată nu se editează direct în sumă — se corectează prin stornarea facturii (la cursul ei original) și emiterea uneia noi, cu cursul BNR corect pentru data operațiunii.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez cursul valutar folosit la o factură în euro?

O factură în euro (sau altă valută) se înregistrează la cursul BNR valabil la data la care intervine exigibilitatea taxei pentru operațiune — de regulă, data facturii. Dacă acest curs a fost greșit la momentul emiterii sau înregistrării, corecția corectă nu e o simplă editare a sumei în lei, ci o stornare urmată de o înregistrare nouă.

## Temeiul legal

::: ghid-temei
„Dacă elementele folosite pentru stabilirea bazei de impozitare a unei operațiuni, alta decât importul de bunuri, se exprimă în valută, cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a României […] valabil la data la care intervine exigibilitatea taxei pentru operațiunea în cauză." — Codul fiscal, art. 290 alin. (2).
:::

## Pașii corecți

1. **Stornarea facturii greșite** — o notă de stornare întoarce sumele cu semn negativ, la **cursul facturii originale**, nu recalculat la cursul de azi. Scopul stornării e să anuleze exact ce a fost înregistrat greșit, nu să introducă o a doua sursă de eroare de curs.
2. **Emiterea unei facturi noi**, corecte, cu cursul BNR valabil la data reală a exigibilității taxei — dacă factura originală a fost deja emisă (și eventual trimisă către client sau prin RO e-Factura), stornarea și noua factură urmează procedura obișnuită de corecție a facturilor deja transmise, nu o editare „în loc" a documentului existent.
3. **Verificarea declarațiilor deja depuse** — dacă factura greșită a fost inclusă într-un decont de TVA sau într-o altă declarație, corecția trebuie reflectată și acolo, nu doar în evidența contabilă curentă.

## Ce se greșește în practică

- Se modifică direct valoarea în lei a facturii, fără stornare, lăsând factura originală (poate deja trimisă clientului sau prin e-Factura) inconsistentă cu evidența contabilă.
- Se folosește la reînregistrare cursul zilei corecției, în loc de cursul valabil la data reală a exigibilității taxei facturii — data de referință rămâne data operațiunii, nu data la care se face corecția.
- Se presupune că o simplă notă explicativă, fără stornare formală, e suficientă pentru a „repara" cursul — fără stornare, urma contabilă a corecției nu e clară, iar sumele rămân duble sau neconcordante.

## Ce face iConta.eu

O stornare în aplicație păstrează exact cursul facturii originale — nu îl recalculează la data stornării — tocmai pentru ca operațiunea de corecție să fie curată: anulează exact ce a fost înregistrat, la aceleași valori. Factura nouă, corectă, se înregistrează separat, cu cursul BNR cerut explicit pentru data ei prin motorul de curs (`core/curs_bnr.py`) — dacă acel curs nu poate fi determinat (monedă necotată, curs indisponibil sau prea vechi), aplicația semnalează explicit problema, nu emite factura cu un curs presupus.

[iConta.eu](/)
