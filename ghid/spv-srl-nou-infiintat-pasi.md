---
title: "SPV pentru SRL nou înființat: pași 2026"
description: "Obligația de înrolare în SPV se aplică oricărei societăți nou înființate, din momentul în care intră sub incidența Codului de procedură fiscală, indiferent de vechime."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# SPV pentru SRL nou înființat: pași 2026

Un SRL proaspăt înființat nu are perioadă de grație pentru înrolarea în SPV — legea nu leagă obligația de o vechime minimă, ci de calitatea de persoană juridică ce trebuie să comunice electronic cu organul fiscal.

## Temeiul legal

::: ghid-temei
„Prin excepţie de la alin. (1), contribuabilii/plătitorii persoane juridice, asocieri şi alte entităţi fără personalitate juridică [...] sunt obligaţi să transmită organului fiscal central documente de natura celor prevăzute la alin. (1) prin mijloace electronice de transmitere la distanţă în condiţiile prezentului articol, respectiv prin înrolarea în sistemul de comunicare electronică dezvoltat de Ministerul Finanţelor/A.N.A.F."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 79 alin. (1^1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Pentru un SRL nou, pașii impuși de lege se reduc, în esență, la doi:

- **Obținerea unui certificat digital calificat** pentru reprezentantul legal (sau un împuternicit desemnat conform art. 18 din aceeași lege) — condiție obligatorie de identificare pentru persoanele juridice (art. 80 alin. (1) lit. a)).
- **Înrolarea** în sistemul de comunicare electronică al Ministerului Finanțelor/ANAF, cu acel certificat — pas care se face direct pe portalul ANAF, conform procedurii tehnice stabilite prin ordin al președintelui ANAF.
- Ulterior, dacă societatea emite facturi și intră sub incidența obligației RO e-Factura (B2B de la înființare, B2C de la 1 ianuarie 2025 pentru toți operatorii economici stabiliți în România), trebuie să se înscrie separat în Registrul RO e-Factura obligatoriu — un pas administrativ distinct de simpla activare SPV.

Nu a fost identificată, în sursele verificate, o derogare sau un termen de grație explicit pentru SRL-urile nou înființate față de această obligație generală — ea se aplică de la momentul la care societatea devine subiect al Codului de procedură fiscală, adică de la înregistrare.

## Ce se greșește în practică

- Se amână obținerea certificatului digital și înrolarea în SPV până la prima obligație declarativă concretă, deși obligația de comunicare electronică există independent de existența unei declarații de depus imediat.
- Se presupune că un SRL nou nu poate fi sancționat pentru neînrolare cât timp nu a avut nicio interacțiune cu ANAF — obligația legală curge de la momentul la care societatea intră sub incidența legii, nu de la prima abatere constatată.
- Se confundă înregistrarea fiscală a societății (obținerea CUI) cu înrolarea în SPV — sunt proceduri diferite, chiar dacă apropiate în timp pentru o firmă nouă.

## Ce face iConta.eu

iConta.eu **nu creează contul SPV** pentru un SRL nou înființat — acest pas rămâne al administratorului/reprezentantului legal, cu certificatul digital calificat, direct pe portalul ANAF. Odată contul SPV activ, iConta.eu oferă conectorul OAuth2 (`core/spv_conector.py`) pentru a-l lega de aplicație, permițând firmei să emită și să primească facturi prin RO e-Factura din interfața de facturare, de la primele operațiuni economice.

[iConta.eu](/)
