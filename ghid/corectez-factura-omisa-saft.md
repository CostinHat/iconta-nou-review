---
title: "Cum corectez o factură omisă din SAF-T?"
description: "Ce prevede Codul de procedură fiscală despre corectarea declarațiilor informative, categorie din care face parte și D406 (SAF-T)."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum corectez o factură omisă din SAF-T?

Declarația informativă D406 (SAF-T) raportează periodic date contabile și fiscale detaliate, inclusiv facturile emise și primite. Dacă se constată ulterior că o factură a lipsit dintr-un fișier deja transmis, corectarea se face prin mecanismul general de rectificare a declarațiilor prevăzut de Codul de procedură fiscală, aplicabil oricărei declarații informative.

## Temeiul legal

::: ghid-temei
„(1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale.
(2) Declarația informativă poate fi corectată de către contribuabil/plătitor indiferent de perioada la care se referă.
(3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 105 alin. (1)-(3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

D406 este, prin natura ei, o declarație informativă (raportează date, nu stabilește direct o obligație de plată), astfel încât i se aplică regula mai permisivă de la alin. (2): poate fi corectată „indiferent de perioada la care se referă" — spre deosebire de declarațiile de impunere, limitate la termenul de prescripție. Corectarea se face, potrivit alin. (3), prin depunerea unei noi declarații rectificative pentru perioada respectivă, care înlocuiește fișierul XML depus inițial cu unul complet, incluzând și factura omisă.

## Ce se greșește în practică

- Se încearcă adăugarea facturii omise doar în declarația D406 a lunii curente, în loc de a rectifica fișierul aferent perioadei în care factura ar fi trebuit raportată inițial.
- Se presupune, greșit, că D406 se supune acelorași limite de timp ca o declarație de impunere (termenul de prescripție) — regimul declarațiilor informative este mai permisiv.
- Se omite verificarea coerenței dintre D406 rectificat și celelalte declarații ale perioadei (de exemplu decontul de TVA), care ar putea necesita, la rândul lor, o corectare separată dacă factura afectează baza de impozitare.

## Ce face iConta.eu

iConta.eu generează fișierul D406 pe baza documentelor introduse în aplicație pentru perioada de raportare. Dacă o factură este adăugată ulterior transmiterii declarației, aplicația poate regenera fișierul aferent perioadei respective, inclusiv factura omisă, pentru retransmitere ca declarație rectificativă; depunerea efectivă a rectificării la ANAF rămâne un pas realizat de utilizator.

[iConta.eu](/)
