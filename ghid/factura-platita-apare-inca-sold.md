---
title: "Ce fac dacă o factură plătită apare încă în sold?"
description: "De ce o plată reală poate rămâne nealocată unei facturi în evidența contabilă și cum se verifică potrivirea extras-factură."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă o factură plătită apare încă în sold?

O factură rămasă „deschisă" în sold, deși clientul sau furnizorul confirmă plata, e aproape întotdeauna o problemă de alocare, nu de contabilitate greșită: banii au intrat sau au ieșit din cont, dar linia din extrasul bancar n-a fost asociată corect cu factura respectivă.

## Temeiul legal

::: ghid-temei
„Documentele justificative trebuie să cuprindă [...] conținutul operațiunii economico-financiare și, atunci când este necesar, temeiul legal al efectuării acesteia [...] datele cantitative și valorice aferente operațiunii economico-financiare efectuate, după caz."
— OMFP 2634/2015, Anexa 1, pct. 2 (sursă: anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt)
:::

Motivele tehnice pentru care o sumă plătită nu stinge factura în evidență:

- **Suma din extras nu se potrivește exact** cu suma facturii (plată parțială, comision bancar dedus, rotunjire) — sistemul de alocare nu poate face o potrivire automată de sumă identică.
- **Lipsește identificatorul de partener** pe linia extrasului (CUI-ul nu apare în descrierea plății) — fără el, o linie de extras nu poate fi legată automat de facturile deschise ale unui anumit partener.
- **Plata a fost alocată altei facturi** a aceluiași partener, prin regula FIFO (facturile cele mai vechi se sting primele) — factura „așteptată" de contabil poate rămâne deschisă, în timp ce o alta mai veche s-a închis cu banii respectivi.
- **Plata există în bancă, dar extrasul n-a fost încă importat/reconciliat** în aplicație — sold-ul contabil nu se actualizează singur, doar prin operațiunea de reconciliere.

## Ce se greșește în practică

- Se marchează manual factura ca „plătită" fără să se verifice de ce potrivirea automată a eșuat — riscul e ca aceeași sumă din extras să rămână, în paralel, nealocată sau alocată greșit altei facturi.
- Se ignoră cazul plăților compuse (o singură plată bancară care acoperă mai multe facturi) — sistemele de alocare simplă, pe sumă identică, nu le recunosc fără o combinație explicită de facturi.
- Se presupune că „banii au ajuns" înseamnă automat că evidența s-a actualizat — între încasarea reală și reconcilierea ei în contabilitate există mereu un pas manual sau de import.

## Ce face iConta.eu

iConta.eu are un motor de reconciliere bancară (`core/reconciliere.py`) care potrivește liniile din extrasul de cont cu facturile deschise ale fiecărui partener: caută întâi o potrivire exactă (o factură sau o combinație de până la 4 facturi cu sumă identică), apoi, dacă nu găsește, alocă suma FIFO pe facturile cele mai vechi. Fiecare linie de extras primește un status vizibil — verde (potrivire exactă), galben (alocare parțială/FIFO, necesită confirmare) sau roșu (fără CUI identificat sau fără facturi deschise ale partenerului) — astfel încât o factură rămasă în sold se poate diagnostica direct din statusul liniei de extras corespunzătoare, nu doar din presupuneri.

[iConta.eu](/)
