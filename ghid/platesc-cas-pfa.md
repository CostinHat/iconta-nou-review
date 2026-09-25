---
title: "Cum plătesc CAS pentru PFA?"
description: "Mecanismul de calcul, declarare și plată a contribuției de asigurări sociale (CAS) datorate de o PFA, potrivit Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum plătesc CAS pentru PFA?

CAS pentru o PFA nu se plătește lunar, prin rețineri, ca la salarii — este un impozit cu autoimpunere: contribuabilul calculează singur contribuția prin aplicarea cotei legale asupra unei baze anuale alese de el (cu un minim obligatoriu), o declară prin Declarația unică (D212) și o plătește până la același termen legal la care depune declarația.

## Temeiul legal

::: ghid-temei
„(1) Contribuabilii prevăzuți la art. 148 alin. (1) și (4) calculează contribuția de asigurări sociale prin aplicarea cotei prevăzute la art. 138 lit. a) asupra bazei anuale de calcul menționate la art. 148 alin. (2), depun Declarația unică privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice până la termenul legal prevăzut la art. 122 alin. (3) și au obligația de a efectua plata acesteia în cadrul aceluiași termen."
— Legea nr. 227/2015 (Codul fiscal), art. 151 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Pașii concreți, așa cum rezultă din art. 148 și 151 din Codul fiscal:

1. **Verifici dacă datorezi CAS**: dacă veniturile nete/normele de venit din activități independente, cumulate cu eventualele venituri din drepturi de proprietate intelectuală, ating cel puțin 12 salarii minime brute pe țară pe an, datorezi CAS (art. 148 alin. (1)).
2. **Alegi baza de calcul**: venitul ales nu poate fi mai mic decât 12 salarii minime brute pe țară (dacă venitul realizat e între 12 și 24 de salarii minime) sau decât 24 de salarii minime brute pe țară (dacă venitul realizat atinge sau depășește acest nivel) — art. 148 alin. (2).
3. **Calculezi CAS**: aplici cota de CAS prevăzută la art. 138 lit. a) asupra bazei anuale alese.
4. **Declari**: completezi capitolul corespunzător din Declarația unică (D212) și o depui până la termenul legal de la art. 122 alin. (3) (25 mai, pentru anul de raportare precedent).
5. **Plătești**: efectuezi plata efectivă a CAS calculate, în același termen în care depui D212 — legea nu prevede plăți eșalonate separate, ci o singură scadență, coincidentă cu termenul de depunere.

## Ce se greșește în practică

- Se plătește CAS lunar sau trimestrial, din obișnuință (ca la salarii sau la unele contribuții ale firmelor), deși pentru PFA legea prevede o singură scadență anuală, coincidentă cu depunerea D212.
- Se alege o bază de calcul sub minimul legal (12 salarii minime brute), ceea ce duce la o CAS calculată greșit, sub cea datorată.
- Se omite verificarea situațiilor speciale — de exemplu, contribuabilii care încep sau încetează activitatea în cursul anului au reguli proprii de calcul proporțional al bazei (art. 151 alin. (2)-(3)).

## Ce face iConta.eu

La data acestui ghid, pentru PFA-urile în sistem real (partidă simplă), iConta.eu calculează baza CAS/CASS din operațiunile validate ale contribuabilului, prin modulul `core/rip_api.py` (funcția `fisa_d212`), folosind plafoanele legale verificate pentru anii acoperiți de aplicație, și generează Declarația unică (D212) prin `core/d212.py`. Aplicația nu efectuează ea însăși plata contribuției către bugetul de stat — plata rămâne un pas separat, realizat de contribuabil, în același termen legal la care se depune D212.

[iConta.eu](/)
