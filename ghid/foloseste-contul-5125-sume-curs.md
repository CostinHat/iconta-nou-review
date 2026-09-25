---
title: "Când se folosește contul 5125 Sume în curs de decontare?"
description: "Regula exactă din OMFP 1802/2014 pentru sumele virate sau depuse la bancă, dar neapărute încă în extrasul de cont: contul 5125, nu contul curent obișnuit."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Când se folosește contul 5125 Sume în curs de decontare?

Contul 5125 rezolvă o problemă concretă de contabilitate bancară: momentul în care banii au fost deja virați sau depuși, dar banca nu i-a înregistrat încă în extrasul de cont al firmei. Reglementările contabile tratează explicit acest interval.

## Temeiul legal

::: ghid-temei
„(2) Sumele virate sau depuse la bănci ori prin mandat poștal, pe bază de documente prezentate entității și neapărute încă în extrasele de cont, se înregistrează distinct în contabilitate (contul 5125 "Sume în curs de decontare")."
— OMFP nr. 1.802/2014 (Reglementări contabile), pct. 302 alin. (2) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Ce rezultă din text pentru utilizarea corectă a contului:

- Contul 5125 se folosește **exclusiv** pentru sumele virate/depuse pe baza unor documente deja prezentate entității (ordin de plată executat, chitanță de depunere), dar care **nu apar încă** în extrasul de cont bancar — nu pentru orice sumă „în tranzit" fără document.
- Este un cont din grupa 51 „Conturi la bănci", alături de 5121 (conturi la bănci în lei) și 5124 (conturi la bănci în valută) — deci rămâne parte din trezoreria firmei, nu o creanță separată.
- Odată ce suma apare în extrasul de cont, ea se transferă din 5125 în contul curent (5121/5124) corespunzător — 5125 este, prin natura lui, tranzitoriu.

## Ce se greșește în practică

- Se folosește contul 5125 pentru orice sumă „neclară", inclusiv pentru avansuri de trezorerie sau debitori diverși, care au conturi proprii distincte (542, respectiv 461) — 5125 e strict pentru operațiuni bancare în curs de confirmare.
- Se lasă solduri vechi în 5125 fără reconciliere ulterioară cu extrasul de cont, ceea ce indică fie o eroare de înregistrare, fie o sumă pierdută în circuitul bancar.
- Se înregistrează direct în contul curent (5121) o sumă pentru care firma are doar dovada virării, nu confirmarea băncii — asta anticipează o mișcare bancară care încă nu s-a produs.

## Ce face iConta.eu

Verificat în cod: `core/plan_omfp.py` include explicit contul „5125": „Sume în curs de decontare" în nomenclatorul de conturi al planului OMFP, alături de „512": „Conturi curente la bănci" — aplicația recunoaște și poate folosi acest cont în înregistrările contabile generate, conform structurii oficiale a planului de conturi.

[iConta.eu](/)
