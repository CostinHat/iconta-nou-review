---
title: "Confuzii frecvente despre plafonul de numerar 2026"
description: "Cele patru plafoane distincte din Legea 70/2015 pentru operațiunile în numerar — și greșelile tipice de a le trata ca pe unul singur."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Confuzii frecvente despre plafonul de numerar 2026

„Plafonul de numerar" nu e o singură cifră — legea stabilește mai multe plafoane distincte, pentru situații diferite (încasare de la o persoană, sold de casă, avans spre decontare, plăți către persoane fizice), și cea mai frecventă greșeală e tratarea lor ca pe unul singur.

## Temeiul legal

::: ghid-temei
„Operațiunile de încasări și plăți efectuate de persoane juridice [...] se vor realiza numai prin instrumente de plată fără numerar [...]. Prin excepție [...] se pot efectua operațiuni de încasări și plăți în numerar, în următoarele condiții: [...] în limita unui plafon zilnic de 5.000 lei de la o persoană; [...] în limita unui plafon zilnic de 10.000 lei de la o persoană [pentru magazinele de tipul cash and carry]; [...] plăți din avansuri spre decontare, în limita unui plafon zilnic de 5.000 lei, stabilit pentru fiecare persoană care a primit avansuri spre decontare. Sunt interzise încasările fragmentate în numerar de la beneficiari pentru facturile a căror valoare este mai mare de 5.000 lei [...], precum și fragmentarea facturilor pentru o livrare de bunuri sau o prestare de servicii a căror valoare este mai mare de 5.000 lei."
— Legea 70/2015, art. 1 alin. (1), art. 3 alin. (1) lit. a), b), e) și alin. (2) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Plafoanele care se confundă cel mai des:

- **5.000 lei/zi de la o persoană** — plafonul standard pentru încasările și plățile în numerar între o firmă și un singur partener (persoană juridică), pe zi.
- **10.000 lei/zi** — plafonul special pentru magazinele de tip cash and carry, mai mare decât cel standard.
- **5.000 lei/zi per persoană** — plafonul separat pentru **avansurile spre decontare** acordate unui angajat; se aplică distinct de plafonul de încasări/plăți cu terții.
- **10.000 lei/zi** — plafonul pentru operațiunile în numerar cu **persoane fizice** (cesiuni de creanțe, împrumuturi, contravaloarea unor livrări/prestări).
- Interdicția de **fragmentare**: o factură peste plafon nu poate fi „spartă" în mai multe încasări/plăți succesive pentru a rămâne sub limită — legea sancționează explicit această practică.

## Ce se greșește în practică

- Se aplică un singur plafon (de regulă cel de 5.000 lei) tuturor situațiilor, ignorând regimul distinct al cash and carry (10.000 lei) sau al operațiunilor cu persoane fizice.
- Se confundă plafonul de sold zilnic al casieriei (suma maximă pe care casieria o poate avea la sfârșitul zilei) cu plafonul de încasare/plată de la un singur partener — sunt reguli diferite, aplicate simultan.
- Se fragmentează plata unei facturi mari în tranșe zilnice succesive sub plafon, crezând că astfel se evită interdicția — legea vizează explicit fragmentarea facturilor și a încasărilor/plăților ca practică sancționabilă.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **verifică automat** toate aceste plafoane: modulul `core/casa.py`, funcția `verifica_plafon`, calculează pe zi soldul casei, încasările și plățile agregate pe fiecare partener persoană juridică (cu regim separat pentru cash and carry), operațiunile cu persoane fizice și avansurile spre decontare, semnalând fiecare depășire ca avertisment (risc la control, nu blocaj al operațiunii). Verificarea acoperă și distincția dintre plafonul standard și cel majorat pentru cash and carry, urmărite separat.

[iConta.eu](/)
