---
title: "Cum corectez D101 dacă am omis o cheltuială nedeductibilă?"
description: "Corectarea D101 după omiterea unei cheltuieli nedeductibile se face prin declarație rectificativă, cu limitele impuse de rezerva verificării ulterioare și de o eventuală inspecție fiscală în curs."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum corectez D101 dacă am omis o cheltuială nedeductibilă?

Dacă, după depunerea D101, descoperi că o cheltuială ar fi trebuit tratată ca nedeductibilă și adăugată înapoi la calculul impozitului pe profit, soluția e depunerea unei declarații rectificative — dar termenul în care poți face asta depinde de rezerva verificării ulterioare și de existența unei inspecții fiscale.

## Temeiul legal

::: ghid-temei
„(1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale. [...] (3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative. [...] (5) Declarația de impunere nu poate fi depusă și nu poate fi corectată după anularea rezervei verificării ulterioare."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 105 alin. (1), (3), (5) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Corectarea se face prin **declarație rectificativă** D101, depusă în cadrul termenului de prescripție a dreptului organului fiscal de a stabili creanțe fiscale.
- Odată **anulată rezerva verificării ulterioare** pentru perioada respectivă (de exemplu în urma unei inspecții fiscale finalizate), declarația nu mai poate fi corectată decât în cazurile excepționale prevăzute la art. 105 alin. (6) — nu prin rectificativă simplă.
- Dacă în timpul corectării ești deja sub **inspecție fiscală** pentru acea perioadă, rectificativa depusă „nu va fi luată în considerare de organul fiscal" — corectarea nu mai are efect, iar cheltuiala nedeductibilă va fi tratată direct de inspectori.
- Corectarea implică recalcularea impozitului pe profit cu cheltuiala readăugată ca nedeductibilă, ceea ce poate genera obligație suplimentară de plată și, după caz, dobânzi de întârziere.

## Ce se greșește în practică

- Se depune rectificativa fără să se verifice dacă rezerva verificării ulterioare a fost deja anulată pentru acea perioadă — caz în care corectarea nu e posibilă pe calea simplă.
- Se așteaptă declanșarea unui control pentru a corecta eroarea, deși descoperirea și corectarea din proprie inițiativă, înainte de inspecție, evită riscul unor sancțiuni suplimentare legate de constatarea erorii de către organul fiscal.
- Se corectează doar suma impozitului fără să se recalculeze corect baza impozabilă (profitul impozabil) care rezultă din readăugarea cheltuielii nedeductibile.

## Ce face iConta.eu

La data acestui ghid, modulul D101 din iConta.eu (`core/d101.py`, `core/d101_reconciliere.py`) calculează și validează declarația pe baza datelor din evidența contabilă a firmei, iar aplicația poate genera din nou formularul după ce o cheltuială e reclasificată drept nedeductibilă în evidență. Nu am găsit însă un flux dedicat de „declarație rectificativă" care să compare automat versiunea inițială cu cea corectată sau care să verifice starea rezervei verificării ulterioare — depunerea efectivă a rectificativei, cu verificarea condițiilor legale de mai sus, rămâne responsabilitatea contabilului.

[iConta.eu](/)
