---
title: "Impozit pe profit pentru firma nou înființată 2026"
description: "Regimul de declarare și plată a impozitului pe profit pentru o firmă nou-înființată în 2026: sistem trimestrial obligatoriu în primul an, plăți anticipate pe profitul contabil real."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Impozit pe profit pentru firma nou înființată 2026

O firmă nou-înființată, plătitoare de impozit pe profit din prima zi, nu poate opta pentru sistemul anual cu plăți anticipate trimestriale — legea o obligă la sistemul trimestrial obișnuit, cu impozit calculat pe profitul real al fiecărui trimestru, nu estimat pe baza unui an anterior care nu există.

## Temeiul legal

::: ghid-temei
„Contribuabilii, alții decât cei prevăzuți la alin. (4) și (5), aplică sistemul de declarare și plată prevăzut la alin. (1) în anul pentru care se datorează impozit pe profit, dacă în anul precedent se încadrează în una dintre următoarele situații: a) au fost nou-înființați, cu excepția contribuabililor nou-înființați ca efect al unor operațiuni de reorganizare efectuate potrivit legii; [...]."
— Legea 227/2015, art. 41 alin. (6) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Calculul, declararea și plata impozitului pe profit, cu excepțiile prevăzute de prezentul articol, se efectuează trimestrial, până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III. Definitivarea și plata impozitului pe profit aferent anului fiscal respectiv se efectuează până la termenul de depunere a declarației privind impozitul pe profit prevăzut la art. 42."
— Legea 227/2015, art. 41 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Anul fiscal este anul calendaristic. [...] Când un contribuabil se înființează [...] în cursul unui an fiscal, perioada impozabilă începe: a) de la data înregistrării acestuia în registrul comerțului [...]."
— Legea 227/2015, art. 16 alin. (1), (3) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Regula practică: o firmă nou-înființată în 2026 intră direct în sistemul trimestrial (art. 41 alin. 1) — calculează și plătește impozit pe profitul real al fiecărui trimestru (I-III), până pe 25 ale lunii următoare, iar definitivarea anuală se face la termenul declarației anuale (art. 42, de regulă 25 martie anul următor). Anul fiscal al firmei începe de la data înregistrării în registrul comerțului (art. 16 alin. 3 lit. a), nu de la 1 ianuarie — perioada impozabilă a primului an e doar fracțiunea rămasă din anul calendaristic.

## Ce se greșește în practică

- Se optează, din start, pentru sistemul anual cu plăți anticipate (art. 41 alin. 2) la o firmă nou-înființată — legea o exclude explicit prin art. 41 alin. (6) lit. a) pentru primul an, tocmai pentru că plățile anticipate se calculează pe baza impozitului anului precedent, care nu există.
- Se calculează primul trimestru de la 1 ianuarie, deși perioada impozabilă începe efectiv de la data înregistrării în registrul comerțului.
- Se confundă „nou-înființată" cu firma rezultată dintr-o reorganizare (fuziune, divizare) — art. 41 alin. (6) lit. a) exclude explicit aceste din urmă situații de la regimul de firmă nouă.

## Ce face iConta.eu

iConta.eu calculează impozitul pe profit al firmei pe baza rezultatului fiscal real (venituri minus cheltuieli), cumulat de la începutul anului fiscal, conform art. 41 — motorul D100 a fost corectat explicit pentru a nu confunda „venituri × cotă" cu „profit × cotă" și pentru a trata corect trecerea de la o obligație de trimestru la alta ca diferență față de ce s-a impozitat deja cumulat. La data acestui ghid, aplicația nu are o verificare automată dedicată a statutului „nou-înființată" al firmei pentru a bloca opțiunea nepermisă pentru sistemul anual în primul an — alegerea sistemului de declarare rămâne o configurare făcută de contabil, pe baza regulilor din art. 41.

[iConta.eu](/)
