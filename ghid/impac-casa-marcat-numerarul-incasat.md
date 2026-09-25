---
title: "Cum împac casa de marcat cu numerarul încasat 2026"
description: "Cum se leagă Raportul Z al casei de marcat electronice fiscale de numerarul efectiv înregistrat în registrul de casă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum împac casa de marcat cu numerarul încasat 2026

Raportul Z de la aparatul de marcat electronic fiscal (AMEF) nu e doar o cifră de „total vânzări" — el defalcă încasările pe modalități de plată (numerar, card, tichete etc.). Doar componenta de numerar din acest raport trebuie să corespundă cu ce intră efectiv în registrul de casă al firmei.

## Temeiul legal

::: ghid-temei
„(2^1) Prin excepție de la prevederile alin. (2), pentru încasările realizate prin utilizarea cardurilor de credit/debit, utilizatorii nu au obligația să imprime/să înmâneze bonuri fiscale cu aparate de marcat electronice fiscale clienților."
— OUG nr. 28/1999, art. 1 alin. (2^1) (sursă: anaf_surse/oug_28_1999.html)
:::

Structura raportului Z, conform formatului standard folosit de AMEF-uri (OPANAF nr. 146/2018), separă vânzările pe tipuri de plată — cod 3 pentru numerar, cod 1 pentru card, plus tichete de masă, bonuri valorice, vouchere și alte instrumente. Pentru reconciliere:

- **Doar valoarea codificată drept „numerar" (tip 3)** din raportul Z trebuie să corespundă cu suma efectiv depusă în casă la finalul zilei.
- Totalul general al raportului Z (vânzări) e mai mare decât suma de numerar, pentru că include și încasările prin card sau alte instrumente, care merg direct în contul bancar, nu în numerar fizic.
- Fiecare cotă de TVA aplicată vânzărilor apare separat în raport, ceea ce permite verificarea și pe acest palier, nu doar pe suma totală.

## Ce se greșește în practică

- Se compară totalul general al raportului Z cu numerarul din casă, deși totalul include și vânzările prin card, care nu ajung fizic în casă.
- Se ignoră faptul că raportul Z separă explicit numerarul pe cod de tip de plată — verificarea se face „la ochi", pe cifra mare, nu pe componenta corectă.
- Se presupune că o diferență între raportul Z și numerarul din casă e mereu o eroare a casei de marcat, fără să se verifice mai întâi dacă operatorul a tastat corect tipul de plată la fiecare vânzare.

## Ce face iConta.eu

iConta.eu importă Raportul Z direct din fișierul exportat de aparatul de marcat electronic fiscal (XML sau format semnat p7b), extrage separat valoarea aferentă fiecărui tip de plată — inclusiv numerarul — și o pune la dispoziție pentru reconcilierea cu registrul de casă, împreună cu defalcarea pe cote de TVA din raport.

[iConta.eu](/)
