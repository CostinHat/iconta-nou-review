---
title: Ce fac dacă am folosit codul TVA greșit în D390?
description: Corectați codul de TVA al partenerului și redepuneți declarația ca rectificativă completă — un cod invalid nu blochează emiterea operațiunii în aplicație, dar afectează scutirea și corectitudinea declarației.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce fac dacă am folosit codul TVA greșit în D390?

Depinde dacă eroarea a fost deja depusă la ANAF sau ați observat-o înainte de depunere.

## Temeiul legal

::: ghid-temei
"Declarația depusă inițial se rectifică prin depunerea unei noi declarații, pe același format, bifând căsuța corespunzătoare de pe formular. În declarația rectificativă se rectifică tranzacții declarate în orice perioadă de raportare anterioară și se completează toate rubricile formularului cu datele valabile la momentul declarării, indiferent dacă acestea au mai fost declarate." — OPANAF nr. 705/2020, Anexa 2, Secțiunea I
:::

::: ghid-temei
"Scutirea prevăzută la alin. (2) lit. a) nu se aplică în cazul în care furnizorul nu a respectat obligația prevăzută la art. 325 alin. (1) de a depune o declarație recapitulativă sau declarația recapitulativă depusă de acesta nu conține informațiile corecte…" — Codul fiscal, art. 294 alin. (2^1)
:::

Dacă observați eroarea **înainte** de depunere, corectați codul TVA al partenerului direct în operațiune, verificați din nou validitatea lui în VIES și regenerați declarația. Dacă declarația a fost **deja depusă** cu codul greșit, corectarea se face prin declarație rectificativă: o declarație nouă, completă, pentru acea lună, cu toate rubricile completate corect, nu doar cu diferența. Legea leagă expres corectitudinea codului de scutirea aplicată la livrare — dacă declarația conține informații incorecte, scutirea aplicată la livrarea de bunuri poate fi pusă în discuție.

## Ce se greșește în practică

- Se lasă operațiunea nemodificată în declarația curentă, considerând eroarea "minoră" — corectitudinea codului TVA are legătură directă cu validitatea scutirii aplicate.
- Se încearcă corectarea prin trecerea liniei pe "0" în loc de o declarație rectificativă completă.
- Se ignoră avertismentul de cod invalid din aplicație, presupunând că e doar o eroare tehnică fără consecințe.

## Ce face iConta.eu

Aplicația verifică validitatea codului de TVA prin interogare VIES live pentru majoritatea statelor UE; doar pentru Germania, Croația și Franța există și o verificare offline suplimentară a cifrei de control. Un cod marcat invalid generează un avertisment, nu un blocaj — operațiunea rămâne emisă, ca să nu dispară tăcut din declarație, dar avertismentul rămâne vizibil până la corectare.

[iConta.eu](/)
