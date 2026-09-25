---
title: "Casierie la firma micro: obligații 2026"
description: "Plafoanele legale pentru încasările și plățile în numerar aplicabile firmelor plătitoare de impozit micro, potrivit Legii nr. 70/2015."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Casierie la firma micro: obligații 2026

Regimul fiscal de micro nu schimbă regulile de casierie — plafoanele pentru numerar sunt aceleași pentru orice persoană juridică, indiferent dacă plătește impozit pe veniturile microîntreprinderilor sau impozit pe profit. Ce diferă e cât de des o firmă mică, cu cifră de afaceri redusă, riscă să le depășească fără să-și dea seama.

## Temeiul legal

::: ghid-temei
„(1) Prin excepție de la prevederile art. 1 alin. (1) se pot efectua operațiuni de încasări și plăți în numerar, în următoarele condiții: a) încasări de la persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei de la o persoană; [...] c) plăți către persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei/persoană, dar nu mai mult de un plafon total de 10.000 lei/zi."
— Legea nr. 70/2015, art. 3 alin. (1) lit. a) și c) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Pentru o firmă mică, plafoanele-cheie de reținut sunt:

- **Încasări/plăți între firme (B2B)**: maximum **5.000 lei/zi de la sau către aceeași persoană**, iar pentru plăți, maximum **10.000 lei total pe zi**, indiferent de câte firme sunt plătite.
- **Încasări/plăți cu persoane fizice (B2C)**: plafonul zilnic urcă la **10.000 lei de la/către o persoană**, conform art. 4 din aceeași lege.
- Fragmentarea unei facturi mai mari decât plafonul, în mai multe încasări/plăți succesive, este expres **interzisă** de lege — inclusiv fragmentarea facturii însăși, nu doar a plății.

## Ce se greșește în practică

- Se aplică din reflex plafonul B2C (10.000 lei) și tranzacțiilor cu alte firme, unde plafonul real este de 5.000 lei/zi.
- Se încasează o factură mare în numerar, în mai multe tranșe pe zile diferite, crezând că astfel se evită plafonul — legea interzice explicit atât încasările fragmentate, cât și fragmentarea facturii pentru o singură livrare sau prestare.
- Se ignoră soldul maxim admis în casieria firmei, distinct de plafoanele de încasare/plată pe tranzacție, ceea ce poate genera o altă neconformitate chiar dacă fiecare încasare respectă plafonul.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are un modul dedicat de casierie (`core/casa.py`) care verifică automat operațiunile în numerar față de plafoanele legale în vigoare pentru 2026 (Legea 70/2015, actualizată prin Legea 239/2025): plafonul de încasare de la persoane juridice, plafonul de plată, plafonul pentru avansuri spre decontare și soldul maxim de casă, semnalând avertismente atunci când o operațiune sau soldul zilei le depășește. Fiecare plafon aplicat este însoțit, în cod, de temeiul legal exact pe care se bazează.

[iConta.eu](/)
