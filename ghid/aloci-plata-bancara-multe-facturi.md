---
title: Cum aloci o plată bancară la mai multe facturi?
description: Reconcilierea bancară din iConta.eu poate lega o singură linie de extras de mai multe facturi deschise ale aceluiași partener — automat, prin combinații exacte sau FIFO, sau manual, din picker.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum aloci o plată bancară la mai multe facturi?

Nu e nevoie ca o încasare sau o plată din extrasul bancar să corespundă exact uneia singure facturi. Când un partener achită mai multe facturi printr-un singur ordin de plată, sau când o plată acoperă parțial facturile cele mai vechi, motorul de reconciliere din iConta.eu poate aloca aceeași linie de extras pe mai multe facturi deschise ale aceluiași partener.

## Temeiul legal

::: ghid-temei
„Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ."
— Legea contabilității nr. 82/1991, art. 6 alin. (1)
:::

::: ghid-temei
„Factura este document justificativ care stă la baza înregistrării în contabilitate a operațiunilor economice. Pentru operațiunile economice pentru care, conform prevederilor Codului fiscal, nu există obligația întocmirii facturii, înregistrarea în contabilitate a acestora se efectuează pe baza contractelor încheiate între părți și a documentelor financiar-contabile sau bancare care să ateste acele operațiuni, cum sunt: [...] extras de cont bancar, notă de contabilitate etc."
— OMFP 2634/2015, Anexa 1 „Norme generale", pct. 25
:::

Legea cere ca fiecare operațiune să aibă un document justificativ, iar extrasul de cont bancar este recunoscut explicit ca atare. Ea nu tranșează însă *câte* facturi poate stinge o singură linie de extras — asta e o chestiune de tehnică de alocare, tratată mai jos.

## Cum alocă iConta.eu o plată pe mai multe facturi

Pentru fiecare linie din extrasul bancar, aplicația caută, în ordine:

1. **Potrivire exactă pe o singură factură** — dacă suma liniei coincide (cu o toleranță de un ban) cu soldul unei facturi deschise a partenerului, se face alocarea 1:1.
2. **Potrivire exactă pe o combinație de facturi** — dacă suma liniei nu se potrivește cu nicio factură singură, dar coincide exact cu suma soldurilor a 2, 3 sau 4 facturi deschise ale aceluiași partener, aplicația propune alocarea pe toate facturile din combinație. Căutarea de combinații se face doar pe primele 12 facturi deschise ale partenerului, în ordinea vechimii — o limită tehnică menită să evite o căutare prea lungă la parteneri cu foarte multe facturi deschise.
3. **Alocare parțială, cea mai veche factură întâi (FIFO)** — dacă nu există nicio potrivire exactă, suma se alocă secvențial pe facturile deschise ale partenerului, de la cea mai veche la cea mai nouă; ultima factură atinsă poate rămâne parțial acoperită. Această alocare cere confirmare manuală înainte de a fi contabilizată.

În oricare din aceste cazuri, alocarea rezultată nu e definitivă automat — contabilul o confirmă din ecranul Bancă înainte ca linia să fie contată.

Pentru situațiile care depășesc automatul (partener cu peste 12 facturi deschise, sau o combinație de sumă care nu iese exact), rămâne disponibil **picker-ul manual** („Alege facturile"): contabilul bifează el însuși facturile pe care le acoperă plata, fără limită de număr.

## Ce se greșește în practică

- Se confirmă o alocare pe combinație fără să se verifice ce facturi conțin efectiv suma propusă — mai ales când suma coincide întâmplător cu o combinație diferită de cea reală.
- Se presupune că motorul găsește orice combinație posibilă, chiar dacă partenerul are mai mult de 12 facturi deschise — dincolo de acest prag, alocarea corectă trebuie făcută manual din picker.
- Se lasă pe „galben" (alocare parțială FIFO) o linie care de fapt acoperă exact alte facturi decât cele mai vechi, fără să se corecteze manual ordinea din picker.

## Ce face iConta.eu

Motorul de potrivire (`core/reconciliere.py`) rulează exact algoritmul descris mai sus — potrivire exactă, combinații de până la 4 facturi din primele 12 deschise ale partenerului, apoi alocare FIFO parțială. Din ecranul „Bancă", butonul „Alege facturile" deschide picker-ul manual, cu bifă pe fiecare factură deschisă a partenerului, pentru cazurile pe care automatul nu le acoperă complet. Contarea propriu-zisă (`core/reconciliere_api.py`) creează, pentru fiecare factură alocată, o notă contabilă separată, legată de acea factură.

[iConta.eu](/)
