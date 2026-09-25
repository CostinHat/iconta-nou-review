---
title: "Cont de trezorerie vs cont bancar comercial"
description: "De ce «trezorerie» și «cont bancar comercial» nu sunt sinonime în contabilitate: clasa 5 din planul de conturi versus un cont curent la bancă, conform OMFP 1802/2014."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cont de trezorerie vs cont bancar comercial

Termenul "cont de trezorerie" apare des în discuții contabile ca și cum ar fi sinonim cu "cont bancar" — dar în planul de conturi general, "trezorerie" e o categorie mult mai largă, iar contul curent la o bancă e doar una dintre componentele ei.

## Temeiul legal

::: ghid-temei
„CLASA 5 - CONTURI DE TREZORERIE GRUPA 50 - INVESTIȚII PE TERMEN SCURT [...] GRUPA 51 - CONTURI LA BĂNCI [...] 5121 Conturi la bănci în lei [...] GRUPA 53 - CASA [...] GRUPA 54 - ACREDITIVE [...] GRUPA 58 - VIRAMENTE INTERNE."
— OMFP 1802/2014, planul de conturi general, clasa 5 „Conturi de trezorerie" (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Distincția, structural:

- **"Conturi de trezorerie" e numele întregii clase 5** din planul de conturi general — acoperă investiții pe termen scurt, conturi la bănci, casa (numerar), acreditive și viramente interne. Termenul contabil "trezorerie" înseamnă, practic, toate disponibilitățile bănești și cvasi-bănești ale firmei.
- **"Cont bancar comercial" e o singură componentă** din această clasă — concret, contul **5121 "Conturi la bănci în lei"** (sau analiticele lui pe fiecare bancă parteneră), grupa 51 "Conturi la bănci".
- Nu există confuzie cu Trezoreria Statului (instituția publică): pentru o firmă privată obișnuită, "cont de trezorerie" în sens contabil se referă la clasa 5 a planului de conturi, nu la conturile deschise la Trezoreria Statului — acestea din urmă privesc, de regulă, instituțiile publice sau anumite plăți către buget.

## Ce se greșește în practică

- Se folosesc cei doi termeni ca sinonimi în discuția curentă, ceea ce nu creează probleme practice, dar generează confuzie când "trezorerie" apare într-un raport financiar (unde înseamnă tot disponibilul, nu doar contul bancar).
- Se omit din calculul "trezoreriei" firmei elementele care nu sunt cont bancar — casa (531), acreditivele (541), investițiile pe termen scurt (50x) — deși toate fac parte din aceeași clasă 5.
- Se confundă "cont de trezorerie" cu un cont deschis la Trezoreria Statului — instituție publică distinctă, nu o categorie a planului de conturi general.

## Ce face iConta.eu

La data acestui ghid, iConta.eu tratează separat cele două module de disponibilități: `core/banca.py`, pentru conturile bancare comerciale (5121/5124), și `core/casa.py`, pentru numerar (5311/5314) și avansuri de trezorerie (542) — ambele fac parte, contabil, din clasa 5 „Conturi de trezorerie". Aplicația nu are un raport consolidat de "trezorerie" care să agrege toate componentele clasei 5 (bancă, casă, avansuri, acreditive) într-o singură cifră de disponibil — fiecare componentă se urmărește azi separat.

[iConta.eu](/)
