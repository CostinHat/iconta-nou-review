---
title: "Ce versiune RO_CIUS se folosește în 2026?"
description: "Ce este specificația RO_CIUS pentru factura electronică, potrivit OUG 120/2021, și limita informației disponibile despre numărul exact de versiune curent."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce versiune RO_CIUS se folosește în 2026?

RO_CIUS e specificația națională de utilizare a facturii electronice, derivată din standardul european EN 16931, care stabilește ce câmpuri și reguli respectă o factură transmisă prin RO e-Factura. Versiunea ei tehnică se schimbă periodic, prin ordine ale ministrului finanțelor, nu prin ordonanța-cadru care instituie sistemul.

## Temeiul legal

::: ghid-temei
„k) specificaţiile naţionale de utilizare a facturii electronice - RO_CIUS - specificaţii tehnice de utilizare a elementelor de bază ale facturii electronice aşa cum sunt prevăzute în standardul european SR EN 16931-1, aplicabile la nivel naţional;"
— OUG 120/2021, art. 2 lit. k) (sursă: anaf_surse/oug_120_2021.txt)

„b) specificaţiile tehnice şi de utilizare a elementelor de bază ale facturii electronice - RO_CIUS - şi regulile operaţionale specifice aplicabile la nivel naţional;"
— OUG 120/2021, art. 4 alin. (1) lit. b) (sursă: anaf_surse/oug_120_2021.txt)
:::

Ce se poate confirma din text:

- **RO_CIUS e definit ca specificația națională de utilizare** a elementelor de bază ale facturii electronice, împreună cu regulile operaționale specifice aplicabile la nivel național — cadrul tehnic prin care România adaptează standardul european EN 16931 la particularitățile fiscale locale (TVA, cote reduse, coduri specifice).
- Ordonanța-cadru (OUG 120/2021) definește **existența și rolul** RO_CIUS, dar **versiunea tehnică exactă** (numărul de versiune al schemei, publicat prin ordin separat al ministrului finanțelor sau prin documentație tehnică ANAF) **nu se regăsește într-o formă citabilă verbatim** în sursele disponibile consultate aici.

**Limitare onestă:** nu pot confirma, din sursele disponibile, numărul exact de versiune RO_CIUS aplicabil în 2026 (ex. „2.0.1" sau altă denumire tehnică) — acest detaliu se schimbă prin acte administrative tehnice, publicate separat de ordonanța-cadru, și trebuie verificat direct pe portalul ANAF/Ministerul Finanțelor la momentul emiterii facturii, nu presupus dintr-o sursă statică.

## Ce se greșește în practică

- Se presupune că versiunea RO_CIUS rămâne fixă de la introducerea sistemului, deși specificația tehnică se actualizează periodic, cu impact asupra validării facturilor transmise.
- Se confundă versiunea RO_CIUS (schema națională) cu versiunea standardului european EN 16931, care e mai stabilă și schimbată mult mai rar.
- Se generează facturi pe o versiune de schemă expirată, respinsă la validare, fără verificarea prealabilă a versiunii curente publicate de ANAF.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **generează facturile electronice conform schemei RO_CIUS curente**, cu validare pe schema ANAF activă la momentul trimiterii (modulul `core/efactura_send.py`, documentat explicit ca „loader pe schema CURENTĂ"), fără a fixa în cod un număr de versiune static care ar deveni rapid depășit. Verificarea versiunii aplicabile se face la momentul trimiterii, direct pe schema publicată de ANAF, nu dintr-o constantă presupusă.

[iConta.eu](/)
