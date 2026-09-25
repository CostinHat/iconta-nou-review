---
title: "Cum transform împrumutul asociatului în capital social?"
description: "Mecanismul legal prin care o creanță a asociatului asupra firmei (împrumut acordat societății) devine aport la majorarea capitalului social, prin compensare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum transform împrumutul asociatului în capital social?

Când un asociat a împrumutat firma (de exemplu prin contul 4551 „Acționari/asociați - conturi curente"), iar firma nu are lichidități pentru a-l restitui, o soluție uzuală este transformarea creanței asociatului în aport la capitalul social. Operațiunea nu este o simplă „mutare contabilă", ci o majorare de capital social prin compensarea unei creanțe lichide și exigibile, supusă regulilor din Legea 31/1990.

## Temeiul legal

::: ghid-temei
„Capitalul social se poate mări prin emisiunea de acțiuni noi sau prin majorarea valorii nominale a acțiunilor existente în schimbul unor noi aporturi în numerar și/sau în natură.
(2) De asemenea, acțiunile noi sunt liberate prin încorporarea rezervelor, cu excepția rezervelor legale, precum și a beneficiilor sau a primelor de emisiune, ori prin compensarea unor creanțe lichide și exigibile asupra societății cu acțiuni ale acesteia."
— Legea nr. 31/1990, art. 210 alin. (1)-(2), Titlul IV „Modificarea actului constitutiv" (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

Articolul se află în titlul dedicat modificării actului constitutiv, aplicabil oricărei forme de societate, nu doar societăților pe acțiuni. Din text rezultă condițiile de fond ale operațiunii:

- Creanța asociatului asupra societății trebuie să fie **lichidă** (cu valoare certă, determinată) și **exigibilă** (scadentă, deci nu un împrumut cu scadență viitoare care încă nu a ajuns la termen).
- Operațiunea presupune o hotărâre a adunării generale de majorare a capitalului social, prin care noile părți sociale/acțiuni sunt liberate prin compensarea creanței, nu prin aport în numerar.
- Contabil, operațiunea presupune stingerea soldului contului de datorie către asociat (ex. 4551) prin creditarea capitalului social (1012), fără flux de numerar efectiv.

## Ce se greșește în practică

- Se tratează transformarea ca pe o simplă notă contabilă, fără hotărârea AGA de majorare a capitalului social și fără modificarea actului constitutiv, deși legea cere parcurgerea procedurii de majorare de capital (inclusiv, după caz, mențiunea la registrul comerțului).
- Se încearcă „transformarea" unei creanțe care nu e încă exigibilă (împrumut cu scadență viitoare) fără o renegociere prealabilă a termenului de rambursare, ceea ce ridică probleme de valabilitate a compensării.
- Se omite verificarea faptului că suma împrumutată a fost efectiv înregistrată și confirmată ca datorie a societății (document justificativ, contract de împrumut, extrase de cont), condiție implicită pentru ca o creanță să fie „lichidă".

## Ce face iConta.eu

iConta.eu gestionează contabil relația curentă cu asociatul (împrumuturi primite de la asociat, dobânzi, restituiri) prin motorul de decontări asociați, care înregistrează automat notele contabile pentru primirea și restituirea unui împrumut de la asociat (5121=4551, respectiv 4551=5121) și impozitarea dobânzii aferente. Transformarea propriu-zisă a soldului 4551 în capital social — operațiune care presupune hotărârea AGA de majorare a capitalului, actul adițional și, după caz, înregistrarea la registrul comerțului — nu este automatizată ca flux dedicat în aplicație; contabilul înregistrează manual nota de compensare după parcurgerea pașilor juridici corespunzători.

[iConta.eu](/)
