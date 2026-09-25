---
title: "Cum se corectează un obiect de inventar înregistrat greșit ca mijloc fix?"
description: "Cum se anulează o amortizare pornită din greșeală pentru un bun care, de fapt, era obiect de inventar, și cum se recunoaște corect cheltuiala integrală."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se corectează un obiect de inventar înregistrat greșit ca mijloc fix?

Situația inversă e la fel de frecventă: un bun sub pragul legal sau cu durată de utilizare sub un an a fost înregistrat, din greșeală, ca mijloc fix și a intrat la amortizare. Aici corecția presupune nu doar reclasificarea bunului, ci și anularea amortizării deja calculate — care n-ar fi trebuit să existe, pentru că bunul respectiv trebuia trecut integral pe cheltuială de la început.

## Temeiul legal

::: ghid-temei
„67. - (1) Corectarea erorilor aferente exercițiului financiar curent se efectuează pe seama contului de profit și pierdere. (2) Corectarea erorilor semnificative aferente exercițiilor financiare precedente se efectuează pe seama rezultatului reportat (contul 1174 «Rezultatul reportat provenit din corectarea erorilor contabile»). (3) Erorile nesemnificative aferente exercițiilor financiare precedente se corectează, de asemenea, pe seama rezultatului reportat. Totuși, potrivit politicilor contabile aprobate, erorile nesemnificative pot fi corectate pe seama contului de profit și pierdere."
— OMFP 1802/2014, reglementări contabile, pct. 67 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.html)
:::

Aplicat la această situație:

- **Se stornează amortizarea deja înregistrată**, pentru că bunul nu îndeplinea, de fapt, condițiile de mijloc fix — amortizarea calculată lunar pe o bază greșită trebuie anulată integral, nu doar corectată de la data descoperirii înainte.
- **Bunul se recunoaște ca obiect de inventar**, cu valoarea lui de intrare trecută integral pe cheltuială (cont 603), conform tratamentului normal al obiectelor de inventar la darea în folosință.
- **Momentul înregistrării erorii decide contul folosit**: eroare din exercițiul curent → contul de profit și pierdere; eroare semnificativă dintr-un exercițiu precedent → rezultatul reportat (1174); eroare nesemnificativă dintr-un exercițiu precedent → rezultatul reportat, sau, dacă politica contabilă aprobată permite, contul de profit și pierdere.
- **Situațiile financiare ale exercițiilor precedente deja depuse nu se modifică** — corectarea nu presupune ajustarea informațiilor comparative din acele situații, ci prezentarea naturii erorii în notele explicative ale exercițiului curent.

## Ce se greșește în practică

- Se oprește doar amortizarea de la data descoperirii înainte, fără să se storneze amortizarea deja înregistrată în lunile/anii anteriori pe o bază greșită.
- Se tratează corecția ca pe o simplă „casare" a mijlocului fix, în loc de o corectare de eroare contabilă — cu consecințe diferite asupra rezultatului reportat.
- Se ignoră pragul de semnificație atunci când eroarea vine dintr-un exercițiu precedent, corectând direct pe cheltuielile perioadei curente o sumă care ar fi trebuit să treacă prin rezultatul reportat.
- Se uită de menționarea naturii erorii și a perioadei afectate în notele explicative la situațiile financiare ale exercițiului în care s-a făcut corectarea.

## Ce face iConta.eu

La fel ca în situația inversă, modulul de obiecte de inventar din iConta.eu acceptă doar operațiile de achiziție, dare în folosință și scoatere din uz — **nu are** o operație dedicată de „reclasificare" sau „corectare" care să anuleze automat o amortizare deja înregistrată greșit pentru un bun care era, de fapt, obiect de inventar. Un concept de reclasificare există în aplicație, dar pentru o cu totul altă situație: trecerea unui stoc între conturi de gestiune (de exemplu, materie primă în marfă), nu trecerea unui activ din categoria mijloc fix în obiect de inventar. Corectarea descrisă mai sus — stornarea amortizării, recunoașterea cheltuielii integrale — rămâne un proces manual, realizat de contabil prin notele contabile generale.

[iConta.eu](/)
