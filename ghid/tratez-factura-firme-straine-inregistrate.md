---
title: "Cum tratez factura unei firme străine înregistrate în scopuri de TVA în România?"
description: "O firmă străină (din UE sau din afara UE) care facturează cu un cod de TVA de România acționează, pentru operațiunea respectivă, ca persoană înregistrată în România — factura urmează regimul intern, nu regimul intracomunitar."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez factura unei firme străine înregistrate în scopuri de TVA în România?

Nu contează unde are sediul social o firmă, ci cu ce cod de TVA a facturat operațiunea. O firmă străină înregistrată direct în scopuri de TVA în România (indiferent dacă e din UE sau din afara UE) poate factura cu codul ei românesc — și atunci operațiunea nu urmează regulile de la achiziții/prestări intracomunitare.

## Temeiul legal

::: ghid-temei
„`desparte_cod_tva(cod)` — separă prefixul de țară de restul codului (...); validează prefixul contra `TARI_UE` (cele 27 state + `XI` = Irlanda de Nord, post-Brexit); erori distincte pentru cod absent / prefix nevalid / prefix fără număr.” — `core/intracomunitar.py`, dosarul F050.
:::

Regimul de achiziție/prestare intracomunitară (art. 268, art. 278 alin. 2) se leagă de un furnizor stabilit și identificat cu un cod de TVA emis de alt stat membru. Dacă firma, deși are sediul în străinătate, a ales să factureze cu cod de TVA românesc (RO), factura urmează regimul intern de TVA — nu se mai verifică în VIES ca operațiune intracomunitară, iar taxa e cea aplicată direct pe factură, nu prin taxare inversă specifică IC.

## Ce se greșește în practică

- Se tratează orice furnizor „străin” ca automat intracomunitar, indiferent de codul de TVA folosit efectiv pe factură.
- Se aplică taxare inversă pe o factură care conține deja TVA colectat cu un cod românesc — riscul e dublarea taxei.
- Se confundă sediul social al firmei (în alt stat) cu identificarea fiscală folosită pentru operațiune (codul de TVA de pe factură) — regimul depinde de a doua, nu de primul.

## Ce face iConta.eu

Verificarea prefixului codului de TVA e primul pas: dacă prefixul e RO, operațiunea nu intră în motorul de operațiuni intracomunitare, indiferent de naționalitatea reală a firmei emitente (prefixul e validat automat contra listei statelor membre UE). Dacă prefixul e al altui stat membru, operațiunea se încadrează ca intracomunitară — verificarea live în VIES e disponibilă în iConta la emiterea facturilor de vânzare; la introducerea unei facturi primite de la un asemenea furnizor, validitatea codului în VIES rămâne de verificat manual de contabil.

[iConta.eu](/)
