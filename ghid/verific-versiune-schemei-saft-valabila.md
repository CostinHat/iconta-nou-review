---
title: "Cum verific ce versiune a schemei SAF-T este valabilă?"
description: "Schema SAF-T (D406) se stabilește prin ordin al președintelui ANAF, iar orice modificare a ei intră în vigoare printr-un ordin nou care înlocuiește sau completează anexa — nu printr-un simplu anunț."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific ce versiune a schemei SAF-T este valabilă?

Fișierul standard de control fiscal (SAF-T, raportat prin declarația D406) are o structură definită oficial, care se modifică ocazional. Ca și în cazul e-Facturii, schimbarea nu e informală — se face printr-un ordin al președintelui ANAF care înlocuiește sau completează anexa cu structura anterioară.

## Temeiul legal

::: ghid-temei
„Art. I - Anexa nr. 5 la Ordinul preşedintelui Agenţiei Naţionale de Administrare Fiscală nr. 1.783/2021 privind natura informaţiilor pe care contribuabilul/plătitorul trebuie să le declare prin fişierul standard de control fiscal, modelul de raportare, procedura şi condiţiile de transmitere, precum şi termenele de transmitere şi data/datele de la care categoriile de contribuabili/plătitori sunt obligate să transmită fişierul standard de control fiscal, publicat în Monitorul Oficial al României, Partea I, nr. 1073 din 9 noiembrie 2021, cu modificările ulterioare, se modifică şi se înlocuieşte cu anexa care face parte integrantă din prezentul ordin."
— OPANAF nr. 407/2025 pentru modificarea anexei nr. 5 la Ordinul preşedintelui ANAF nr. 1.783/2021, art. I (sursă: anaf_surse/opanaf_407_2025_saft_d406.txt)
:::

Ce arată acest text despre cum se verifică versiunea corectă:

- Structura de bază a SAF-T rămâne cea din **OPANAF 1.783/2021**, actul normativ inițial care a introdus obligația.
- Fiecare modificare ulterioară (ca OPANAF 407/2025, care înlocuiește integral anexa nr. 5 privind termenele/categoriile de contribuabili) e un act separat, publicat în Monitorul Oficial, care se aplică **peste** actul inițial, nu îl abrogă în întregime.
- Verificarea versiunii valabile la un moment dat înseamnă, deci, identificarea OPANAF 1.783/2021 plus toate ordinele care l-au modificat până la data raportării — nu doar consultarea celui mai recent document găsit, care ar putea viza doar o anexă (de exemplu, doar termenele, nu structura XML propriu-zisă).
- Sursa tehnică finală (structura XML/XSD exactă) e publicată de ANAF ca document separat, dar valabilitatea ei juridică derivă tot din ordinul care o aprobă — un XSD descărcat fără ordinul care îl susține nu e, singur, dovada versiunii corecte.

## Ce se greșește în practică

- Se folosește un XSD sau un document de structură vechi, presupunând că SAF-T "nu s-a schimbat de la introducere" — deși anexele tehnice au fost modificate de mai multe ori (cum arată chiar OPANAF 407/2025).
- Se confundă modificarea termenelor de depunere (cine și când trebuie să depună D406) cu modificarea structurii XML propriu-zise a fișierului — cele două pot fi actualizate prin ordine diferite, la momente diferite.
- Se validează local fișierul D406 pe o schemă neactualizată, iar prima confirmare a schimbării vine abia la respingerea depunerii de către ANAF.

## Ce face iConta.eu

Generarea declarației D406 (SAF-T) în iConta.eu produce structura XML pe baza schemei oficiale curente, verificată direct pe validatorul ANAF instalat, secțiune cu secțiune (inclusiv sub-secțiunea de active/amortizare). Aplicația nu are însă un mecanism de alertare automată atunci când ANAF publică un ordin nou care modifică schema — actualizarea generatorului la o schemă nouă e un proces intern, declanșat manual, la apariția modificării oficiale.

[iConta.eu](/)
