---
title: "Ce faci dacă ai omis venituri din calculul impozitului micro?"
description: "Cum se corectează, potrivit Codului de procedură fiscală, o declarație de impunere pentru impozitul pe veniturile microîntreprinderilor în care au fost omise venituri."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce faci dacă ai omis venituri din calculul impozitului micro?

Omiterea unor venituri din baza de calcul a impozitului pe veniturile microîntreprinderilor nu se remediază printr-o notă internă sau printr-o compensare tacită la trimestrul următor — Codul de procedură fiscală prevede un mecanism explicit de corectare a declarației deja depuse.

## Temeiul legal

::: ghid-temei
„ART. 105 Corectarea declarației fiscale
(1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale.
[...]
(3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 105 alin. (1) și (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce înseamnă acest temei pentru veniturile omise la impozitul micro:

- Corectarea se face prin **declarație rectificativă**, depusă pentru perioada (trimestrul) în care venitul a fost efectiv realizat și omis — nu prin includerea lui „compensatoriu" în declarația trimestrului curent.
- Termenul-limită pentru corectare este **termenul de prescripție a dreptului organului fiscal de a stabili creanțe fiscale**, nu un termen scurt de câteva zile — dar cu cât corectarea se face mai devreme, cu atât riscul de accesorii (dobânzi/penalități) e mai mic.
- Dacă diferența de impozit rezultată din declarația rectificativă e stabilită de contribuabil, termenul de plată al diferenței este chiar data depunerii declarației rectificative la organul fiscal (art. 156 alin. (4) din același cod).

## Ce se greșește în practică

- Se „ajustează" venitul trimestrului curent pentru a compensa omisiunea din trimestrul anterior, în loc să se depună o declarație rectificativă pentru perioada corectă — asta denaturează ambele perioade.
- Se amână corectarea sperând că eroarea nu va fi observată, deși dobânzile de întârziere curg din momentul scadenței inițiale, nu din momentul descoperirii.
- Se confundă declarația rectificativă pentru impozitul micro cu o simplă explicație transmisă ANAF — corectarea trebuie făcută prin formularul propriu-zis (D100, cu bifa de rectificativă), nu printr-o adresă.

## Ce face iConta.eu

Verificat în cod: `core/test_a8_micro_baza.py` și `core/test_note_explicative_micro.py` arată că baza impozitului micro este calculată din datele contabile curente ale trimestrului; iConta.eu nu are, la acest moment, un asistent dedicat pentru generarea automată a unei declarații D100 rectificative în cazul unor venituri omise dintr-un trimestru anterior — o astfel de corecție se face manual, prin recalcularea trimestrului respectiv și redepunerea declarației.

[iConta.eu](/)
