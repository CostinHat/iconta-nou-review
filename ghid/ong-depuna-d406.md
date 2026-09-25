---
title: "Un ONG trebuie să depună D406?"
description: "Asociațiile și persoanele fără scop patrimonial figurează explicit printre categoriile obligate să depună fișierul standard de control fiscal (SAF-T) prin Declarația informativă D406."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Un ONG trebuie să depună D406?

Declarația informativă D406, prin care se transmite fișierul standard de control fiscal (SAF-T), nu e o obligație rezervată societăților comerciale. Ordinul care reglementează SAF-T listează explicit categoriile de contribuabili vizate, iar organizațiile nonprofit apar pe această listă.

## Temeiul legal

::: ghid-temei
„3. Următoarele categorii de contribuabili au obligaţia de depunere a fişierului standard de control fiscal (SAF-T), prin intermediul Declaraţiei informative D406: [...] - asociaţiile cu scop patrimonial; - asociaţiile/persoanele fără scop patrimonial; [...] - alte persoane juridice, care nu se regăsesc menţionate în mod expres la pct. 4."
— OPANAF 1783/2021, Anexa 5, pct. 3 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

- Lista de la pct. 3 include explicit **asociațiile și persoanele fără scop patrimonial** printre categoriile obligate să depună D406 — nu e o obligație limitată la societățile comerciale (SRL, SA etc.).
- Data de la care obligația devine efectivă depinde de categoria de contribuabil (mari, mijlocii, mici), stabilită potrivit clasificării ANAF, nu de forma juridică: contribuabilii mari raportează din 2022, cei mijlocii din 2023, cei mici din 2025, iar cei nou-înregistrați ulterior datei de referință raportează de la data efectivă a înregistrării în categoria respectivă.
- Ordinul prevede și o listă separată de entități **exceptate** (PFA, întreprinderi individuale, întreprinderi familiale, cabinete de avocat/notar/medic, instituții publice) — organizațiile nonprofit **nu se regăsesc** în această listă de excepții.

## Ce se greșește în practică

- Se presupune că D406/SAF-T e o obligație doar pentru societăți comerciale mari — de fapt privește categoria de contribuabil (mare/mijlociu/mic), care se stabilește indiferent de forma juridică, iar asociațiile/fundațiile sunt listate explicit ca obligate.
- Se ignoră obligația pentru simplul motiv că organizația nu are activitate economică semnificativă — încadrarea în categoria de contribuabil se face după criterii ANAF, nu după volumul activității economice a unui ONG.
- Se confundă data de referință a categoriei (mari/mijlocii/mici) cu data înființării organizației — un ONG nou-înființat raportează de la data efectivă a înregistrării în categoria sa, ulterioară datei de referință generale.

## Ce face iConta.eu

Funcționalitatea de contabilitate ONG din iConta.eu (`core/ong.py`) se ocupă exclusiv de înregistrarea veniturilor fără scop patrimonial pe conturile din grupa 73 și de calculul scutirii de impozit pe profit potrivit art. 15 Cod fiscal — **nu generează și nu depune Declarația D406/SAF-T**; niciun modul legat de contabilitatea ONG nu atinge fișierul standard de control fiscal. Dacă organizația are obligația D406, aceasta se gestionează, dacă e disponibilă, prin modulele generale de raportare ale aplicației, independent de această funcționalitate.

[iConta.eu](/)
