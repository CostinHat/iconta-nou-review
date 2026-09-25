---
title: "Ce fac dacă am omis o chitanță din registrul de casă?"
description: "Regula legală a completării zilnice a Registrului de casă și cum se remediază onest o chitanță rămasă în afara lui."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă am omis o chitanță din registrul de casă?

Registrul de casă trebuie să reflecte, zi de zi, exact ce a intrat și ce a ieșit din casierie în numerar. Când o chitanță — încasare sau plată — rămâne pe dinafară, soldul de casă din registru nu mai corespunde cu numerarul real, iar diferența trebuie găsită și corectată cât mai repede.

## Temeiul legal

::: ghid-temei
„Registrul de casă servește ca: document de înregistrare operativă a încasărilor și plăților în numerar (lei sau valută), efectuate prin casieria entității; document de stabilire, la sfârșitul fiecărei zile, a soldului de casă; document de înregistrare în contabilitate a operațiunilor de casă. Registrul de casă se întocmește zilnic, pe baza documentelor justificative de încasări și plăți."
— OMFP 2634/2015, Anexa 2 „Norme specifice", Grupa IV, Registrul de casă (Cod 14-4-7) (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

- Registrul de casă nu e un document care se completează „la final de lună" sau „când ai timp" — norma spune explicit că **se întocmește zilnic**, pe baza documentelor justificative (inclusiv chitanțele) ale zilei respective.
- Fiecare operațiune de casă trebuie susținută de documentul ei justificativ — o chitanță omisă înseamnă că soldul de casă calculat la sfârșitul zilei omisiunii, și al tuturor zilelor următoare, e greșit până la corectare.
- Corectarea unei omisiuni cere reconstituirea ordinii cronologice reale: chitanța se introduce la data ei efectivă, iar soldurile zilnice ulterioare, calculate din acel punct înainte, trebuie recalculate în consecință.

## Ce se greșește în practică

- Chitanța omisă e adăugată în registru cu data zilei în care a fost observată lipsa, nu cu data reală a operațiunii — ceea ce denaturează soldurile zilnice intermediare.
- Se corectează doar soldul final, fără să se refacă și soldurile de casă ale zilelor cuprinse între data reală a chitanței și data descoperirii omisiunii.
- Diferența dintre numerarul fizic din casă și soldul din registru e „ajustată" direct, fără să se identifice și să se documenteze cauza (chitanța lipsă), ceea ce lasă evidența nejustificată la un eventual control.

## Ce face iConta.eu

Funcționalitatea F017 din iConta.eu acoperă **emiterea** de chitanțe de către firmă (`chitanta_emite`) — care înregistrează automat operațiunea de casă (5311=4111) în chiar momentul emiterii — și, separat, **certificarea** unei chitanțe primite de la un furnizor prin fluxul de portal (`chitanta_stinge`, cont 401=5311), care cere ca documentul să fi fost deja încărcat și confirmat de client. Niciunul din aceste două fluxuri, verificate în cod, nu oferă o funcție dedicată de „adăugare retroactivă" a unei chitanțe omise, cu recalcularea automată a soldurilor de casă din zilele intermediare — acest tip de corecție rămâne, la acest moment, un pas manual, în afara aplicației.

[iConta.eu](/)
