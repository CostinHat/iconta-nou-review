---
title: "Greșeala de a nu factura la timp"
description: "Termenul legal maxim de emitere a facturii — cea de-a 15-a zi a lunii următoare faptului generator — și de ce depășirea lui nu e doar o problemă de disciplină internă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Greșeala de a nu factura la timp

„O emit când am timp" e răspunsul cel mai frecvent dat de firmele care amână facturarea. Problema e că legea fixează un termen maxim pentru emiterea facturii, iar depășirea lui afectează atât exigibilitatea TVA, cât și corectitudinea perioadei fiscale în care operațiunea trebuie raportată.

## Temeiul legal

::: ghid-temei
„(16) Pentru alte operațiuni decât cele prevăzute la alin. (15), persoana impozabilă are obligația de a emite o factură cel târziu până în cea de-a 15-a zi a lunii următoare celei în care ia naștere faptul generator al taxei, cu excepția cazului în care factura a fost deja emisă. De asemenea, persoana impozabilă trebuie să emită o factură pentru suma avansurilor încasate în legătură cu o livrare de bunuri/prestare de servicii cel târziu până în cea de-a 15-a zi a lunii următoare celei în care a încasat avansurile, cu excepția cazului în care factura a fost deja emisă."
— Legea nr. 227/2015 (Codul fiscal), art. 319 alin. (16) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce trebuie reținut din regulă:

- Termenul de emitere nu e „până la sfârșitul lunii curente", ci **cel târziu în a 15-a zi a lunii următoare** celei în care s-a produs faptul generator (de regulă livrarea bunurilor sau prestarea serviciilor) — un interval mai generos decât se crede, dar tot un termen ferm, nu orientativ.
- Regula se aplică identic **avansurilor încasate** — chiar dacă nu a avut loc încă livrarea/prestarea, avansul trebuie facturat până în a 15-a zi a lunii următoare încasării lui.
- Pentru livrările intracomunitare de bunuri (alin. (15)), termenul e același — a 15-a zi a lunii următoare faptului generator — dar regula e separată de cea generală, pentru că livrările intracomunitare au propriile obligații de raportare (D390).
- Emiterea facturii cu întârziere nu schimbă faptul generator al taxei — exigibilitatea TVA rămâne legată de data faptului generator (sau de încasarea avansului), nu de data la care factura a fost, în cele din urmă, emisă; întârzierea creează însă riscul raportării TVA în perioada greșită și expune firma la sancțiuni contravenționale.

## Ce se greșește în practică

- Se emit facturile în lot, la finalul lunii sau chiar în luna următoare celei în care ar fi trebuit emise, fără să se verifice dacă s-a depășit termenul de 15 zile din luna următoare faptului generator.
- Se consideră că avansurile nu trebuie facturate separat dacă factura finală „vine oricum în curând" — deși legea impune facturarea avansului în același termen ca orice altă operațiune.
- Se raportează TVA în luna emiterii facturii, nu în luna faptului generator, ceea ce poate decala greșit exigibilitatea taxei față de perioada fiscală corectă.

## Ce face iConta.eu

La data acestui ghid, iConta.eu permite emiterea facturilor din aplicație (`core/facturi.py`, `core/facturi_api.py`), cu numerotare secvențială și calcul automat al TVA pe baza datei introduse. Aplicația **nu blochează și nu atenționează automat** atunci când o factură e emisă cu întârziere față de termenul legal de 15 zile de la faptul generator — data faptului generator, comparată cu termenul legal de emitere, rămâne o verificare pe care contabilul trebuie să o facă manual, la fiecare emitere.

[iConta.eu](/)
