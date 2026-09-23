---
title: Cum tratez o livrare intracomunitară fără cod TVA valid
description: Fără cod de TVA valid al clientului din UE, livrarea nu se poate scuti — se facturează cu TVA românesc, ca o livrare internă, indiferent dacă transportul în alt stat membru e dovedit.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum tratez o livrare intracomunitară fără cod TVA valid

Vinzi bunuri unui client din alt stat membru, dar codul lui de TVA nu e valid — a fost anulat, suspendat, sau firma nu e înregistrată pentru operațiuni intracomunitare. Scutirea de TVA nu se poate aplica, oricât de sigur ai fi că bunurile chiar au plecat din România.

## Temeiul legal

::: ghid-temei
„`valideaza_lic(cod_tva_client, cod_valid_vies, are_dovada_transport)` — validează condițiile scutirii LIC (art. 294 alin. 2 lit. a): client non-RO + cod valid VIES + dovadă transport; fără oricare din ele → eroare explicită «facturează cu TVA».” — cod sursă `core/intracomunitar.py`, verificat în dosarul F050; temei: CF art. 294 alin. (2) lit. a).
:::

Cele două condiții ale scutirii — cod valid comunicat de client + dovada transportului — sunt cumulative. Codul nevalid rupe scutirea de unul singur, indiferent dacă ai și dovada transportului.

## Ce faci concret

**Facturezi cu TVA din România**, la cota aplicabilă bunului vândut, exact ca la o livrare internă către un client fără cod valid de TVA. Operațiunea nu se declară în D390 — declarația recapitulativă privește livrările intracomunitare scutite, iar aceasta nu se califică drept una.

**Nu tratezi operațiunea ca livrare intracomunitară în evidență** — încadrarea greșită (scutit, fără TVA) produce o diferență care apare fie la controlul încrucișat intern, fie, mai grav, la o inspecție ANAF, ca TVA nedeclarată.

**Verifici din nou codul, ulterior.** Dacă înregistrarea clientului în VIES se rezolvă și codul devine valid pentru o operațiune viitoare cu același partener, aceea se poate factura scutit — dar operațiunea deja facturată cu TVA rămâne așa; nu se corectează retroactiv doar pentru că partenerul și-a rezolvat ulterior înregistrarea.

## Ce se greșește în practică

Cea mai costisitoare greșeală e facturarea scutită „pe încredere”, fără verificare VIES la data facturii, urmată de descoperirea ulterioară că a existat o perioadă în care codul clientului nu era valid. Corectarea presupune stornarea facturii, reemiterea cu TVA și, dacă operațiunea a fost deja raportată, o declarație rectificativă de D390. A doua greșeală: se confundă „firma clientului există, are cod de TVA în țara ei” cu „codul e valid pentru operațiuni intracomunitare” — sunt lucruri diferite, iar doar al doilea contează pentru scutire.

## Ce face iConta.eu

La emiterea facturii către un client cu cod de TVA de prefix non-românesc, sistemul verifică automat starea codului în VIES și afișează rezultatul. Motorul intern al operațiunilor intracomunitare validează explicit condițiile scutirii — cod valid + dovadă transport — iar când codul nu e valid, întoarce o eroare clară care indică ce lipsește: operațiunea nu se poate încadra ca livrare intracomunitară scutită și trebuie facturată cu TVA.

[iConta.eu](/)
