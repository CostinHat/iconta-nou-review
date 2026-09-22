---
title: Cum aloci o încasare bancară la mai multe facturi?
description: Legea cere doar ca operațiunea să aibă un document justificativ; ordinea exactă în care se sting facturile deschise ale unui partener (FIFO, cele mai vechi întâi) e logica aplicației, nu un text de lege citat verbatim.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum aloci o încasare bancară la mai multe facturi?

Când un client plătește printr-o singură linie de extras o sumă care acoperă mai multe facturi deschise, apare întrebarea firească: pe care facturi se stinge suma și în ce ordine? Motorul de matching din iConta.eu rezolvă acest caz automat, dar merită înțeles exact ce face și pe ce se bazează.

## Temeiul legal

::: ghid-temei
**Articolul 6 (1)** Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ. **(2)** Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz.

**Art. 1620 - Imputația.** Atunci când mai multe obligații susceptibile de compensație sunt datorate de același debitor, regulile stabilite pentru imputația plății se aplică în mod corespunzător.
:::

## Cum decide motorul ce facturi se sting

Pentru fiecare linie de extras cu CUI identificat, motorul caută mai întâi o factură deschisă a partenerului a cărei sold diferă de suma liniei cu cel mult 0,01 lei — dacă o găsește, o închide integral. Dacă nu, caută o combinație de 2-4 facturi ale aceluiași partener a căror sumă de solduri cade exact (±0,01 lei) pe suma liniei; preferă combinațiile mai mici și facturile mai vechi. Dacă nici combinația exactă nu există, suma se alocă secvențial pe facturile deschise ale partenerului, în ordinea vechimii (FIFO) — cele mai vechi facturi se sting primele, iar ultima factură atinsă poate rămâne parțial acoperită.

::: ghid-exemplu
Un client are trei facturi deschise, emise pe rând, cu solduri de 500, 800 și 300 lei. Vine o încasare de 1.300 lei. Motorul nu găsește potrivire exactă pe o singură factură, dar găsește combinația 500 + 800 = 1.300 lei — stinge exact aceste două facturi, iar cea de 300 lei rămâne deschisă.
:::

Important de precizat onest: ordinea FIFO (facturile cele mai vechi întâi) este o decizie de logică a aplicației, consecventă cu principiul general de imputație a plății din Codul civil (art. 1620 trimite la "regulile imputației plății"), dar textul efectiv al acestor reguli nu a putut fi confirmat verbatim în sursele legale verificate. Nu există, deci, o normă explicită care să impună exact ordinea FIFO — e o practică rezonabilă de produs.

## Ce se greșește în practică

- Se așteaptă ca sistemul să găsească orice combinație de facturi care însumează suma plătită, indiferent de câte facturi sunt implicate — motorul caută combinații exacte doar pentru 2-4 facturi.
- Se presupune că, la volume mari de facturi deschise (peste 12), motorul le ia pe toate în calcul la căutarea combinației exacte — de fapt căutarea se limitează la primele 12 facturi FIFO, ca protecție împotriva unui calcul exploziv.
- Se confundă alocarea automată FIFO cu o regulă legală obligatorie — e o alegere de produs, nu o normă din Codul civil sau din Legea contabilității.
- Se ignoră faptul că o factură alocată parțial la o linie de extras nu mai e disponibilă în același cuantum la linia următoare din același extras.

## Ce face iConta.eu

Motorul de matching (`core/reconciliere.py`) parcurge, pentru fiecare linie de extras cu CUI identificat, în ordine: potrivire exactă pe o singură factură (toleranță 0,01 lei), apoi potrivire exactă pe o combinație de 2-4 facturi (`MAX_COMBO = 4`, căutare limitată la primele 12 facturi FIFO ale partenerului), apoi alocare parțială FIFO pe soldurile rămase. Facturile eligibile sunt filtrate strict pe CUI-ul normalizat al partenerului și pe direcția corespunzătoare tipului liniei (încasare → facturi emise; plată → facturi primite) și sortate FIFO după data emiterii.

Rezultatul unei potriviri exacte (una sau combo) primește status verde; alocarea parțială FIFO primește status galben și necesită confirmare manuală înainte de contare. La contare (`conteaza`), utilizatorul poate suprascrie alocările sugerate de motor prin parametrul `alocari`, dacă vrea o altă repartizare decât cea propusă automat.

[iConta.eu](/)
