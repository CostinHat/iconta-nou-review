---
title: "Cum contabilizez un transfer între două conturi bancare ale aceleiași firme?"
description: Această întrebare nu ține de transferul de stocuri între gestiuni. E vorba de mișcare de bani între două conturi bancare, subiect diferit - contul 581 și evidența de trezorerie, nu evidența de marfă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum contabilizez un transfer între două conturi bancare ale aceleiași firme?

Această întrebare nu are legătură cu transferul de marfă între gestiuni (F138) — e un transfer de bani între două conturi bancare deținute de aceeași firmă, subiect din zona de trezorerie, nu din zona de stocuri. Le tratăm distinct pentru că documentele, conturile și mecanismul de raportare sunt complet diferite.

## Temeiul legal

::: ghid-temei
„Pentru operațiunile economice pentru care, conform prevederilor Codului fiscal, nu există obligația întocmirii facturii, înregistrarea în contabilitate a acestora se efectuează pe baza contractelor încheiate între părți și a documentelor financiar-contabile sau bancare care să ateste acele operațiuni, cum sunt: aviz de însoțire a mărfii, chitanță, dispoziție de plată/încasare, extras de cont bancar, notă de contabilitate etc., după caz."

— OMFP 2634/2015, Anexa 1 (Norme generale), pct. 25
:::

Textul confirmă un singur lucru direct relevant aici: extrasul de cont bancar e document justificativ suficient pentru o operațiune fără factură, categorie în care intră și un transfer între conturi bancare proprii. Nu confirmă însă tratamentul contabil complet (conturi, notă contabilă) pentru acest tip de operațiune — acela ține de capitolul de trezorerie al reglementărilor contabile (OMFP 1802/2014) și de planul de conturi, pe care nu l-am verificat punct cu punct pentru acest subiect. Uzual, un asemenea transfer se înregistrează prin contul 581 „Viramente interne", cu două note (ieșire din contul sursă în 581, intrare din 581 în contul destinație), dar recomandăm confirmarea exactă cu un consultant contabil sau cu reglementarea de trezorerie înainte de a considera acest paragraf temei complet.

## Ce se greșește în practică

- Se caută acest subiect sub eticheta „transfer între gestiuni" sau F138 — sunt funcționalități complet diferite; F138 mută marfă între locații de stoc, nu bani între conturi.
- Se lasă transferul bancar necategorizat sau categorizat greșit ca „achiziție"/"încasare", ceea ce denaturează situația de trezorerie și poate duplica venituri sau cheltuieli.
- Se presupune că orice mișcare între conturile proprii ale firmei e recunoscută automat de sistemul contabil ca „virament intern" — depinde de modul de categorizare configurat, vezi mai jos.

## Ce face iConta.eu

Important de precizat, ca să nu creeze o așteptare greșită: în iConta.eu, contul 581 „Viramente interne" e legat, în motorul de categorizare automată a extraselor bancare, **strict de operațiuni de numerar** — tranzacții al căror text conține cuvinte-cheie ca „retragere", „ATM", „ridicare numerar", „depunere numerar" sau „alimentare". Verificat direct în codul de categorizare: nu există un cuvânt-cheie sau o regulă dedicată pentru „transfer între conturi bancare proprii" în sens general (de exemplu „virament", „alimentare cont", „între conturi"). Deci un transfer obișnuit bancă-la-bancă între două conturi ale aceleiași firme **nu e recunoscut automat** de categorizarea curentă a aplicației — va fi nevoie să-l categorizați manual pe contul 581, sau conform indicației contabilului dvs., dacă tratamentul diferă.

Pentru subiectul de stocuri și transfer între gestiuni, vedeți [ghidul despre transferul de stocuri între gestiuni: documente](/ghid/GH-03089).

[iConta.eu](/)
