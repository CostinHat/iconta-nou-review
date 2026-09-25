---
title: "Pot depune mai multe declarații D212 rectificative?"
description: "Ce spune Codul de procedură fiscală despre numărul de declarații rectificative D212 pe care le poate depune un contribuabil și termenul-limită până la care poate corecta declarația."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Pot depune mai multe declarații D212 rectificative?

Da. Legea nu limitează numărul de declarații rectificative pe care le poate depune un contribuabil pentru D212 — condiția este ca fiecare corecție să se facă în interiorul termenului de prescripție a dreptului organului fiscal de a stabili creanțe fiscale.

## Temeiul legal

::: ghid-temei
„(1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale.
[...]
(3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 105 alin. (1), (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă din text:

- Nu există în lege o limită numerică pentru declarațiile rectificative — art. 105 alin. (1) fixează doar limita temporală: termenul de prescripție a dreptului organului fiscal de a stabili creanțe fiscale (de regulă 5 ani, potrivit dispozițiilor generale ale Codului de procedură fiscală privind prescripția).
- Fiecare corecție se face prin depunerea unei noi declarații rectificative (art. 105 alin. (3)), care înlocuiește, pentru elementele corectate, datele declarate anterior.
- Există totuși o limită de altă natură: art. 105 alin. (5)-(6) prevede că declarația de impunere nu mai poate fi depusă sau corectată **după anularea rezervei verificării ulterioare**, cu excepția unor situații expres reglementate (de exemplu, îndeplinirea/neîndeplinirea unei condiții legale sau hotărâri judecătorești definitive care modifică baza de impozitare).

## Ce se greșește în practică

- Se crede că D212 poate fi rectificată o singură dată sau de un număr limitat de ori — legea nu impune o astfel de restricție, în interiorul termenului de prescripție.
- Se depune o rectificativă după ce a fost anulată rezerva verificării ulterioare asupra perioadei respective, fără verificarea prealabilă a excepțiilor de la art. 105 alin. (6) care ar permite totuși corecția.
- Se ignoră faptul că o rectificativă depusă în timpul unei inspecții fiscale, pentru perioadele și creanțele ce fac obiectul acelei inspecții, nu este luată în considerare de organul fiscal (art. 105 alin. (8)).

## Ce face iConta.eu

La data acestui ghid, iConta.eu poate genera D212 marcată drept declarație rectificativă: modulul `core/d212.py` include atributele `rectif1` și `rectif2` din structura oficială a formularului, pe care contabilul le poate seta la generarea fiecărei variante corectate. Aplicația nu ține însă un istoric automat al declarațiilor rectificative deja depuse la ANAF și nu verifică dacă rezerva verificării ulterioare a fost anulată pentru perioada respectivă — aceste aspecte rămân responsabilitatea contabilului.

[iConta.eu](/)
