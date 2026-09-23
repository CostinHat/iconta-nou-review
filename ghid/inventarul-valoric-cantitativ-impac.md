---
title: "Inventarul valoric și cel cantitativ: cum le împac"
description: "Diferența dintre gestiunea global-valorică (la preț de vânzare) și cea cantitativ-valorică (la cost mediu ponderat), și cum pot coexista în aceeași firmă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Inventarul valoric și cel cantitativ: cum le împac

O firmă poate avea, simultan, stocuri ținute prin metode diferite: unele la preț de vânzare cu amănuntul (evidență global-valorică), altele pe cantități și costuri individuale (evidență cantitativ-valorică). Legea permite asta, cu condiția aplicării consecvente a fiecărei metode pe categoria ei de stocuri.

## Temeiul legal

::: ghid-temei
OMFP 1802/2014, Anexa 1 — Reglementări contabile, pct. 286 alin. (1): „... pentru determinarea costului pot fi folosite, de asemenea, metoda costului standard, în activitatea de producție sau metoda prețului cu amănuntul, în comerțul cu amănuntul."

(Text consolidat OMFP 1802/2014, verificat pe mirrorul local la 17.09.2026.)
:::

Pe lângă metoda prețului cu amănuntul (global-valorică), reglementările prevăd la pct. 287 alin. (1)-(4) — rezumat din dosarul de cercetare, nu citat literal — obligația de a aplica metoda aleasă consecvent între exerciții, iar schimbarea ei presupune un motiv și prezentarea efectelor în notele explicative; totodată, se poate justifica folosirea unor metode diferite pentru stocuri cu natură sau utilizare diferită în cadrul aceleiași firme.

Practic, cele două metode nu se „amestecă" pe același stoc: fiecare categorie de stocuri (de exemplu marfă vândută la raft, respectiv materii prime sau produse din rețete) se ține consecvent printr-o singură metodă.

## Ce se greșește în practică

- Se încearcă aplicarea simultană a ambelor metode pe aceeași categorie de stocuri, ceea ce contrazice cerința de consecvență.
- Se presupune că metoda cantitativ-valorică (cost mediu ponderat) și metoda global-valorică (preț cu amănuntul) produc aceleași conturi și aceleași note contabile — de fapt, gestiunea cantitativ-valorică nu folosește conturile 378 (adaos comercial) și 4428 (TVA neexigibilă), specifice metodei global-valorice.

## Ce face iConta.eu

iConta.eu are două motoare de calcul separate pentru cele două metode:

- **Gestiune global-valorică** (`core/stocuri.py`, `core/stocuri_api.py`): calculează coeficientul de repartizare (K) și generează lunar nota de descărcare (607/378/4428), pe baza rulajelor cumulate de la 1 ianuarie.
- **Gestiune cantitativ-valorică — CMP** (`core/stocuri_cv.py`, `core/stocuri_cv_api.py`): recalculează costul mediu ponderat după fiecare intrare, ține o fișă de magazie cronologică per articol și validează cronologic ieșirile, astfel încât o ieșire nu poate depăși stocul existent la data ei (note 607 = 371 pentru marfă, 601 = 301 pentru materii prime).

Cele două mecanisme funcționează independent, pe categorii de stocuri diferite din aceeași firmă, fără cod comun între ele: conform cercetării care stă la baza acestui ghid, nu există în `core/stocuri.py` sau `core/stocuri_cv.py` nicio referință una către cealaltă. Alegerea metodei, pentru fiecare gestiune în parte, rămâne o decizie a contabilului, aplicată consecvent.

[iConta.eu](/)
