---
title: "Cum se înlocuiește casa de marcat defectă"
description: "Termenul de 72 de ore în care distribuitorul autorizat trebuie să instaleze un aparat nou sau să înlocuiască memoria fiscală, conform OUG 28/1999."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înlocuiește casa de marcat defectă

Odată notificat, distribuitorul autorizat nu are libertate nelimitată de a stabili când repară sau înlocuiește aparatul — legea îi impune un termen fix.

## Temeiul legal

::: ghid-temei
„(5) Distribuitorii autorizați, precum și unitățile din rețeaua acestora acreditate pentru service, după caz, au obligația să asigure, în termen de maximum 72 de ore de la solicitarea utilizatorului, instalarea aparatului nou, precum și înlocuirea memoriei fiscale sau a dispozitivului de memorare a jurnalului electronic în cazul în care sunt defecte sau capacitatea de stocare a fost epuizată."
— OUG 28/1999, art. 5 alin. (5) (sursă: anaf_surse/oug_28_1999.html)
:::

Ce garantează norma:

- **Termenul e de maximum 72 de ore de la solicitarea utilizatorului** — nu de la data constatării defecțiunii de către distribuitor, ci de la momentul la care utilizatorul a cerut intervenția.
- Obligația acoperă atât **instalarea unui aparat nou**, cât și **înlocuirea memoriei fiscale sau a dispozitivului de memorare a jurnalului electronic**, dacă acestea sunt defecte sau capacitatea de stocare a fost epuizată — deci nu doar cazul aparatului complet nefuncțional.
- Obligația e a **distribuitorului autorizat sau a unității de service acreditate a acestuia** — utilizatorul nu poate apela la orice tehnician, ci trebuie să rămână în rețeaua autorizată legată de aparatul respectiv.
- În intervalul de până la 72 de ore (sau chiar mai mult, dacă intervenția întârzie), rămâne aplicabilă procedura alternativă de la art. 1 alin. (8): registru special și chitanțe, până la repunerea efectivă în funcțiune.

## Ce se greșește în practică

- Se acceptă tacit întârzieri mari ale distribuitorului, fără a invoca termenul legal de 72 de ore — utilizatorul are dreptul să ceară respectarea lui, cu dovada notificării făcute conform art. 1 alin. (8^1).
- Se cumpără sau se instalează un aparat de la alt furnizor decât distribuitorul autorizat inițial, pentru viteză — încalcă regula rețelei autorizate, cu riscuri suplimentare privind memoria fiscală și cartea de intervenții.
- Se consideră perioada de așteptare a distribuitorului drept "timp mort" pentru activitatea comercială — legea permite continuarea vânzărilor pe toată durata reparației, prin registrul special.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu are un modul care să urmărească termenul de 72 de ore al distribuitorului sau să gestioneze comunicarea cu unitatea de service acreditată — aceasta rămâne o relație contractuală directă între utilizator și distribuitorul autorizat al aparatului. Ce oferă aplicația e evidența contabilă generală care continuă să funcționeze indiferent de starea AMEF, prin `core/chitante.py` pentru documentele emise pe perioada de indisponibilitate.

[iConta.eu](/)
