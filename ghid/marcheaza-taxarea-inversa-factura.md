---
title: "Cum se marchează taxarea inversă în e-Factura?"
description: Legea cere o singură mențiune explicită pe factură — „taxare inversă” — obligatorie în sarcina furnizorului; lipsa ei duce, la beneficiar, la pierderea dreptului de deducere.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se marchează taxarea inversă în e-Factura?

Indiferent de canalul prin care circulă factura, marcarea cerută de lege e simplă: furnizorul are obligația să înscrie pe factură mențiunea „taxare inversă", fără taxa colectată aferentă. Restul — cum anume se codifică acest lucru tehnic în fișierul RO e-Factura — ține de formatul de transmitere, nu de regula de fond.

## Temeiul legal

::: ghid-temei
„Furnizorul/Prestatorul are obligația să înscrie pe factură mențiunea „taxare inversă"."
— HG 1/2016, pct. 109 alin. (1)
:::

::: ghid-temei
„În cazul neaplicării taxării inverse prevăzute de lege, respectiv în situația în care furnizorul/prestatorul emite o factură cu TVA pentru operațiunile prevăzute la art. 331 alin. (2) din Codul fiscal și nu înscrie mențiunea „taxare inversă" în respectiva factură, iar beneficiarul deduce taxa înscrisă în factură, acesta își pierde dreptul de deducere pentru achiziția respectivă de bunuri sau servicii deoarece condițiile de fond privind taxarea inversă nu au fost respectate și factura a fost întocmită în mod eronat."
— HG 1/2016, pct. 109 alin. (4)
:::

Miza practică a mențiunii nu e formală — e o condiție de fond. Dacă factura ar fi trebuit emisă cu taxare inversă (operațiune de la art. 331 alin. (2), ambele părți plătitoare de TVA, categorie neexpirată, prag valoric îndeplinit unde e cazul), dar furnizorul a scris TVA în loc de mențiune, iar beneficiarul a dedus acea TVA, beneficiarul pierde dreptul de deducere — chiar dacă eroarea aparține furnizorului. Norma se aplică inclusiv atunci când corectarea nu mai e posibilă din cauza falimentului furnizorului.

**Notă**: sursele verificate pentru acest ghid confirmă obligația legală a mențiunii și consecința ei, dar nu acoperă structura exactă a câmpurilor din fișierul XML RO e-Factura în care se codifică tehnic această mențiune — pentru formatul tehnic exact, verifică documentația RO e-Factura.

## Ce se greșește în practică

- Se emite factura cu TVA normal pe o operațiune care ar fi trebuit taxată invers, iar beneficiarul deduce taxa fără să verifice dacă operațiunea se încadra la art. 331 alin. (2).
- Se presupune că „taxare inversă" e doar o informație contabilă internă, nu o mențiune obligatorie pe factura propriu-zisă.
- Se corectează eroarea doar contabil, la beneficiar, fără să se solicite furnizorului o factură corectată cu mențiunea corectă.

## Ce face iConta.eu

Când operațiunea îndeplinește condițiile de la art. 331 (categorie validă, ambele părți plătitoare de TVA, termen și prag respectate acolo unde se aplică), aplicația generează automat, la beneficiar, nota `4426=4427` și populează rândurile corespunzătoare din D300 și D394, tratând operațiunea ca fiind corect marcată. Aplicația nu verifică independent dacă furnizorul a scris efectiv mențiunea pe factura fizică/PDF primită — dacă ai suspiciuni că o factură a fost emisă eronat, cu TVA în loc de mențiune, verifică direct documentul primit înainte de a înregistra deducerea.

[iConta.eu](/)
