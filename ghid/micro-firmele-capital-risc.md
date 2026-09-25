---
title: "Micro și firmele cu capital de risc"
description: "Limitare importantă: legea nu exclude firmele cu investitori de tip capital de risc de la regimul micro pe acest temei explicit, dar impune reguli de agregare a veniturilor pentru acționarii care dețin peste 25%."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Micro și firmele cu capital de risc

Nu există, în sursele verificate, o excludere explicită de la regimul de impozitare a microîntreprinderilor pentru firmele care au printre acționari un fond de capital de risc (venture capital/private equity). Ce există, în schimb, este o regulă generală de agregare a veniturilor pentru asociații/acționarii care dețin participații semnificative — relevantă dacă un astfel de fond deține peste 25% din companie.

## Temeiul legal

::: ghid-temei
„Nu intră sub incidența prezentului titlu următoarele persoane juridice române: [...] f) persoana juridică română care desfășoară activități în domeniul bancar; [...] g) persoana juridică română care desfășoară activități în domeniul asigurărilor și reasigurărilor, al pieței de capital, precum și persoana juridică română care desfășoară activități de intermediere/distribuție în aceste domenii [...]"
— Legea nr. 227/2015 (Codul fiscal), art. 47 alin. (3) lit. f)-g) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Limitare onestă: art. 47 alin. (3) exclude de la regimul micro persoanele juridice care **ele însele** desfășoară activități bancare, de asigurări sau de piață de capital — nu firmele care au, printre acționari, un fond de capital de risc. Nu am găsit în corpus o excludere specifică pentru acest din urmă caz. Ce e relevant, în schimb:

- Art. 47 alin. (1) lit. h) și alin. (1^1) impun ca, atunci când asociații/acționarii unei microîntreprinderi dețin, direct sau indirect, **peste 25%** din titlurile de participare sau drepturile de vot la mai multe firme eligibile pentru regimul micro, aceștia trebuie să stabilească o singură persoană juridică ce aplică regimul micro, iar veniturile firmelor „legate" se agregă pentru verificarea plafonului.
- Dacă un fond de capital de risc deține o participație de peste 25% în mai multe portofolii eligibile pentru micro, regula de agregare a veniturilor „întreprinderilor legate" (art. 47 alin. (1^1)) poate deveni relevantă pentru verificarea plafonului de venituri al fiecărei firme din portofoliu.
- O firmă rămâne eligibilă pentru regimul micro atât timp cât nu se încadrează la niciuna dintre excluderile explicite de la art. 47 alin. (3) (bancar, asigurări, piață de capital, jocuri de noroc, petrol și gaze) — simpla prezență a unui investitor de tip capital de risc nu figurează printre acestea.

## Ce se greșește în practică

- Se presupune că prezența unui fond de investiții/capital de risc printre acționari exclude automat firma de la regimul micro — nu există un asemenea temei explicit în textul verificat.
- Se ignoră regula de agregare a veniturilor pentru acționarii cu peste 25%, care poate afecta indirect eligibilitatea pentru micro dacă fondul deține participații mari în mai multe firme.
- Se confundă activitatea „de piață de capital" a unei societăți (exclusă explicit la lit. g) cu simplul fapt de a avea un acționar activ pe piața de capital (fondul de investiții) — sunt situații diferite.

## Ce face iConta.eu

Verificat în cod: `core/test_a8_micro_baza.py` arată doar cum se calculează baza impozabilă trimestrială a impozitului micro (venituri din orice sursă minus 709) — nu există, la acest moment, o verificare automată a eligibilității propriu-zise pentru regimul micro (regimul fiscal e un câmp declarat manual, la Date firmă). iConta.eu nu are nici o funcție de agregare automată a veniturilor între firme „legate" prin acționari comuni care dețin peste 25% (regula art. 47 alin. (1^1)) — o astfel de verificare rămâne, deocamdată, în responsabilitatea contabilului.

[iConta.eu](/)
