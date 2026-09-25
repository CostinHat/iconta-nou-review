---
title: "Impactul unei singure întârzieri asupra scorului fiscal al firmei"
description: "Ce este, legal, «scorul fiscal» al unei firme — clasa de risc fiscal stabilită de ANAF — și ce spune legea despre modul în care se calculează și se contestă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Impactul unei singure întârzieri asupra scorului fiscal al firmei

Ce numim colocvial „scor fiscal" corespunde, legal, clasei/subclasei de risc fiscal în care ANAF încadrează fiecare contribuabil, pe baza unei analize de risc. Această clasificare influențează direct procedurile de administrare aplicate firmei, inclusiv probabilitatea unei inspecții.

## Temeiul legal

::: ghid-temei
„În cazul creanțelor fiscale administrate de organul fiscal central, procedurile de administrare se realizează în funcție de clasa/subclasa de risc fiscal în care sunt încadrați contribuabilii ca urmare a analizei de risc efectuate de organul fiscal. [...] Contribuabilul nu poate face obiecții cu privire la modul de stabilire a riscului și a clasei/subclasei de risc fiscal în care a fost încadrat."
— Legea 207/2015 (Codul de procedură fiscală), art. 7 alin. (5) și alin. (11) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce se poate spune, cu certitudine, din text:

- Contribuabilii sunt împărțiți în 3 clase principale: risc fiscal mic, mediu și ridicat (art. 7 alin. 6), dezvoltate la rândul lor în subclase, pe criterii aprobate prin ordin al președintelui ANAF (art. 7 alin. 8) — deci **neaflate în textul public al legii**.
- Analiza de risc se efectuează periodic, iar clasa/subclasa se comunică contribuabilului doar la cererea acestuia (art. 7 alin. 10).
- Contribuabilii cu risc fiscal ridicat care nu remediază, în termenul comunicat, riscurile pentru care au fost notificați sunt supuși **obligatoriu** unei inspecții fiscale sau unei verificări documentare (art. 7 alin. 4, coroborat cu alin. 2).

## Ce se greșește în practică

- Se așteaptă un răspuns cert la întrebarea „câte puncte pierde firma la o întârziere" — criteriile generale sunt stabilite prin ordin ANAF, nepublic în detaliu ca formulă, deci nu există o cifră legală de citat pentru impactul exact al unei singure întârzieri.
- Se presupune că un singur incident de conformare (o declarație depusă cu o zi întârziere, de exemplu) schimbă automat clasa de risc — legea vorbește despre o analiză periodică, pe criterii multiple, nu despre un declanșator unic documentat public.
- Se încearcă contestarea încadrării într-o clasă de risc considerată nedreaptă — legea exclude explicit acest drept (art. 7 alin. 11).

## Ce face iConta.eu

iConta.eu nu are acces la criteriile interne de risc fiscal ale ANAF și nu calculează sau estimează „scorul fiscal" al unei firme — aceste criterii nu sunt publice. Aplicația oferă însă un motor propriu de urmărire a conformării declarative (`core/control_fiscal_api.py`, `core/alerte_control_fiscal.py`), care semnalează declarațiile lipsă, depuse fără obligație sau contradictorii — tocmai genul de neconcordanțe care, în practică, cresc probabilitatea unei încadrări nefavorabile la analiza de risc a organului fiscal, fără ca aplicația să pretindă că reproduce acea analiză.

[iConta.eu](/)
