---
title: Ce fac dacă am compensat greșit două facturi?
description: Contează ce înțelegi prin „compensare" — alocarea greșită a unei încasări/plăți pe facturi (F073) se corectează diferit față de compensarea legală reciprocă dintre o creanță și o datorie, pe care F073 nu o automatizează.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce fac dacă am compensat greșit două facturi?

Cuvântul „compensare" se folosește în practică în două sensuri diferite, iar corectarea diferă după caz.

## Temeiul legal

::: ghid-temei
„Datoriile reciproce se sting prin compensație până la concurența celei mai mici dintre ele."
— Codul civil (Legea 287/2009), art. 1616
:::

::: ghid-temei
„Compensația operează de plin drept de îndată ce există două datorii certe, lichide și exigibile, oricare ar fi izvorul lor, și care au ca obiect o sumă de bani sau o anumită cantitate de bunuri fungibile de aceeași natură."
— Codul civil (Legea 287/2009), art. 1617 alin. (1)
:::

::: ghid-temei
„Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz."
— Legea contabilității nr. 82/1991, art. 6 alin. (2)
:::

## Cele două sensuri ale „compensării"

1. **„Compensare" ca alocare automată** — sensul colocvial folosit adesea pentru mecanismul motorului de reconciliere din iConta.eu: o încasare/plată din extras stinge automat una sau mai multe facturi ale aceluiași partener, pe aceeași direcție (o încasare stinge facturi emise, o plată stinge facturi primite). Dacă alocarea automată a „stins" greșit facturile care nu trebuiau, corectarea urmează mecanismul obișnuit: ștergerea notei dacă e încă ciornă (linia de extras revine pe „potrivit", gata de realocare), sau dezlegarea notei de factură dacă a fost deja validată (cu rol de administrator și motiv obligatoriu), urmată de crearea manuală a notei corecte.

2. **„Compensare" în sensul legal** — stingerea reciprocă a unei creanțe cu o datorie față de același partener (de exemplu, un partener care e simultan client și furnizor al firmei), reglementată de Codul civil, art. 1616-1623. **Acest mecanism nu este implementat în motorul de reconciliere bancară**: motorul lucrează mereu pe o singură direcție per linie de extras — o încasare potrivește doar facturi emise, o plată potrivește doar facturi primite — și nu stinge niciodată o factură emisă contra unei facturi primite de la același partener. O compensare legală reciprocă se înregistrează separat, ca notă de jurnal manuală (401 = 4111), în afara reconcilierii bancare.

## Ce se greșește în practică

- Se caută în ecranul Bancă un mecanism de „anulare a compensării" pentru o compensare legală reciprocă (client-furnizor) — acest tip de operațiune nu trece niciodată prin reconcilierea bancară, deci corectarea ei nu se face de acolo.
- Se corectează o alocare greșită a unei încasări pe facturi (sensul 1) crezând că e vorba de compensare legală (sensul 2), ceea ce duce la căutarea unei soluții mult mai complicate decât e nevoie.
- Se presupune că aplicația verifică automat condițiile legale ale compensației (creanțe certe, lichide, exigibile) — nu există o astfel de verificare automată, pentru că mecanismul nu e implementat.

## Ce face iConta.eu

Pentru alocarea automată greșită a unei încasări/plăți pe facturi (sensul colocvial), corectarea se face prin ștergerea notei ciornă sau dezlegarea notei validate, ca la orice alocare greșită din reconciliere. Pentru compensarea legală reciprocă între o creanță și o datorie față de același partener, iConta.eu nu are un mecanism automat — operațiunea se înregistrează manual, ca notă de jurnal (401 = 4111), cu documentul de compensare corespunzător ca justificare.

[iConta.eu](/)
