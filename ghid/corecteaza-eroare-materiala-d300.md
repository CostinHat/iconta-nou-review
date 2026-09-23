---
title: "Cum se corectează o eroare materială din D300?"
description: Erorile materiale din D300 (fără impact asupra cuantumului taxei) au o procedură de corecție separată de regularizarea obișnuită — aprobată prin ordin ANAF, al cărui conținut exact nu face parte din sursele verificate ale acestui ghid.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se corectează o eroare materială din D300?

Legea face o distincție clară: erorile care schimbă suma de TVA datorată se corectează prin regularizare într-un decont ulterior, dar erorile pur materiale — cele care nu modifică cuantumul taxei — au o procedură proprie, separată.

## Temeiul legal

::: ghid-temei
**Art. 105 alin. (4) Cod de procedură fiscală (Legea 207/2015):** *„... în cazul taxei pe valoarea adăugată, corectarea erorilor din deconturile de taxă se realizează potrivit prevederilor Codului fiscal [art. 323 alin. (3)]. Erorile materiale din decontul de TVA se corectează potrivit procedurii aprobate prin ordin al preşedintelui A.N.A.F."*
:::

## Ce știm sigur și ce nu

Ce e confirmat de sursele verificate: legea distinge explicit între corectarea erorilor de fond (prin regularizare în decontul unei perioade ulterioare, conform art. 323 alin. (3) Cod fiscal) și corectarea erorilor materiale (printr-o procedură separată, aprobată prin ordin al președintelui ANAF).

Ce nu putem confirma aici: conținutul exact al acelui ordin ANAF — procedura pas cu pas de corectare a erorilor materiale. Textul integral al ordinului nu face parte din sursele verificate pentru acest ghid, așa că nu reproducem detalii despre formularul sau pașii ceruți de el, ca să nu riscăm o citare inventată.

Ce poate ajuta la încadrare: o eroare e „materială" atunci când nu schimbă suma de TVA colectată, dedusă sau de plată/recuperat — de exemplu o greșeală de transcriere a unui CIF, a unei denumiri sau a unei perioade, care nu afectează cifrele decontului. Dacă eroarea modifică orice sumă din decont, nu mai e o eroare materială — intră la regularizarea obișnuită, prin decontul unei perioade ulterioare.

## Ce se greșește în practică

- **Se tratează orice greșeală de completare drept „eroare materială"**, inclusiv una care schimbă o sumă din decont — doar erorile fără impact asupra cuantumului taxei intră la această procedură.
- **Se aplică regularizarea obișnuită (rândurile de regularizări dintr-un decont ulterior) și pentru erori pur materiale** — cele două proceduri sunt distincte prevăzute separat de lege.
- **Se caută detaliile procedurii de corecție a erorilor materiale în Codul fiscal** — procedura e reglementată printr-un ordin ANAF separat, nu în Codul fiscal.

## Ce face iConta.eu

Aplicația nu are, în acest moment, un flux dedicat pentru procedura specifică de corecție a erorilor materiale (distinctă de regularizarea de fond) — panoul manual de regularizări TVA (`core/d300_manual_api.py`) acoperă corecțiile care afectează cuantumul taxei, prin decontul unei perioade ulterioare. Pentru o eroare pur materială, verificarea procedurii exacte rămâne o discuție cu organul fiscal sau cu un consultant care are acces la textul ordinului ANAF aplicabil.

[iConta.eu](/)
