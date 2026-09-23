---
title: Ce fac dacă firma trebuia să treacă la impozit pe profit, dar a rămas micro?
description: Depășirea plafonului de 100.000 euro obligă trecerea la impozit pe profit chiar din trimestrul depășirii — iar aplicația nu detectează automat momentul, corectarea fiind manuală.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce fac dacă firma trebuia să treacă la impozit pe profit, dar a rămas micro?

Dacă firma a depășit plafonul de venituri pentru microîntreprindere și a continuat totuși să depună declarații de micro, obligația legală s-a născut deja — problema acum e să identifici corect trimestrul și să corectezi vectorul retroactiv.

## Temeiul legal

::: ghid-temei
**Art. 52 alin. (1) CF** „Reguli de ieșire din sistemul de impunere pe veniturile microîntreprinderilor în cursul anului": „Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit **începând cu trimestrul în care s-a depășit această limită**." Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, linia 6414 (modificat de OUG 8/2026, art. 6 pct. 20).
:::

Obligația de trecere la impozit pe profit nu e opțională și nu așteaptă finalul anului — curge de la trimestrul concret în care veniturile cumulate au depășit 100.000 euro (calculat la cursul de schimb valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile, conform art. 47 alin. 1 lit. c). Dacă firma a continuat să depună D100 (micro) în loc de D101 (profit) după acel moment, declarațiile depuse pentru trimestrele ulterioare depășirii au fost pe regimul greșit.

Corecția are doi pași: identifici exact trimestrul depășirii, cumulând veniturile de la începutul anului, apoi schimbi `regim_fiscal` din „micro" în „profit" în Vectorul fiscal al firmei, cu data de aplicare corectă. Dacă în acest interval firma are deja perioade fiscale închise (declarații deja depuse și blocate), schimbarea vectorului e refuzată direct de aplicație până redeschizi acele perioade.

Corectarea declarațiilor deja depuse la ANAF (rectificative D100/D101) e un pas separat, de făcut direct la ANAF/SPV — vectorul din iConta e o evidență internă, nu transmite nimic automat către ANAF.

## Ce se greșește în practică

- Se presupune că trecerea la profit se face abia din anul următor, nu din trimestrul efectiv al depășirii, așa cum cere explicit art. 52 alin. (1).
- Se așteaptă o alertă automată din aplicație la depășirea plafonului — iConta nu are nicio constantă de plafon micro în motor și nu detectează automat depășirea.
- Se schimbă doar vectorul pentru viitor, fără să se corecteze retroactiv trimestrele deja raportate greșit ca micro.

## Ce face iConta.eu

Motorul (`core/control_fiscal_api.py`) confirmă explicit, în comentariu de cod: „Aplicația NU cunoaște plafonul de ieșire din micro [...], deci nu există fapt care să contrazică bifa; atunci blocajul rămâne, dar spune UNDE se corectează." Nu există nicio constantă de plafon micro (100.000 €) în motorul de calcul — verificarea depășirii e integral responsabilitatea contabilului. Schimbarea efectivă a `regim_fiscal` e o editare manuală în Vector fiscal, supusă regulii care blochează modificarea peste perioade fiscale deja închise (trebuie redeschisă perioada, schimbat vectorul, apoi închisă la loc).

[iConta.eu](/)
