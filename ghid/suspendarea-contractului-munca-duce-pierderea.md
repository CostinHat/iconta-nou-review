---
title: "Suspendarea contractului de muncă duce la pierderea regimului micro?"
description: "Ce se întâmplă cu încadrarea la impozitul pe veniturile microîntreprinderilor atunci când singurul salariat al firmei are contractul de muncă suspendat, potrivit Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Suspendarea contractului de muncă duce la pierderea regimului micro?

Nu automat — dar nici fără limită. Legea a introdus în 2026 o regulă explicită pentru situația în care singurul salariat al unui SRL plătitor de impozit micro intră în suspendare: contează durata suspendării, nu simplul fapt că a avut loc.

## Temeiul legal

::: ghid-temei
„În sensul prezentului titlu, în cazul în care raportul de muncă este suspendat, potrivit legii, condiția prevăzută la art. 47 alin. (1) lit. g) se consideră îndeplinită dacă perioada de suspendare este mai mică de 30 de zile și situația este înregistrată pentru prima dată în anul fiscal respectiv. În caz contrar sunt aplicabile, în mod corespunzător, dispozițiile art. 52 alin. (3)."
— Legea nr. 227/2015 (Codul fiscal), art. 48 alin. (3^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Practic, condiția de la art. 47 alin. (1) lit. g) — „are cel puțin un salariat" — rămâne îndeplinită în timpul suspendării doar dacă:

- perioada de suspendare este **mai mică de 30 de zile**; și
- este **prima suspendare** înregistrată în anul fiscal respectiv la acea firmă.
- Dacă oricare din aceste două condiții nu este respectată, firma nu mai îndeplinește condiția de salariat și devine, în mod corespunzător, plătitoare de impozit pe profit — conform mecanismului de ieșire forțată de la art. 52 alin. (3), care prevede și o soluție de salvare: angajarea unui nou salariat în 30 de zile de la încetarea raportului de muncă.
- Legea are în vedere inclusiv concediul medical: art. 48 alin. (3^3) tratează separat incapacitatea temporară de muncă, tot cu un prag cumulat de 30 de zile pe an.

## Ce se greșește în practică

- Se presupune că orice suspendare a contractului de muncă (concediu fără plată, concediu pentru creșterea copilului, incapacitate temporară) scoate automat firma din regimul micro — de fapt, sub 30 de zile și la prima apariție din an, condiția rămâne îndeplinită.
- Se ignoră cumulul: dacă în cursul aceluiași an apar mai multe suspendări, chiar scurte, doar prima beneficiază de excepție; se cumulează pragul, nu se resetează la fiecare suspendare nouă.
- Se confundă suspendarea contractului cu încetarea lui — regulile de „înlocuire în 30 de zile" de la art. 52 alin. (3) privesc încetarea raportului de muncă, nu suspendarea temporară.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu calculează automat** impactul unei suspendări de contract asupra eligibilității pentru regimul micro. Aplicația păstrează, în profilul firmei, un câmp de regim fiscal (`micro`/`profit`, vezi `core/vector_fiscal_api.py`) pe baza căruia generează declarațiile corespunzătoare (D100 trimestrial pentru micro, D101 anual pentru profit), dar nu urmărește zilele de suspendare ale contractelor de muncă și nu alertează contabilul când pragul de 30 de zile este depășit. Verificarea condiției de salariat, în cazul suspendărilor, rămâne o evaluare manuală a contabilului.

[iConta.eu](/)
