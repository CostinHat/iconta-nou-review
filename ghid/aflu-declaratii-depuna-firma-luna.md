---
title: Cum aflu ce declarații trebuie să depună firma luna aceasta?
description: Semaforul de conformare fiscală răspunde exact la această întrebare — pentru fiecare firmă, câte o pastilă și motivul din spatele ei, nu o listă generică valabilă pentru toată lumea.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum aflu ce declarații trebuie să depună firma luna aceasta?

Lista declarațiilor datorate într-o lună anume diferă de la firmă la firmă: depinde de regimul fiscal, de statutul de TVA și de periodicitatea lui, și de faptul dacă firma are sau nu salariați activi în luna respectivă. Nu e o listă fixă, universală, valabilă pentru orice firmă.

## Temeiul legal

::: ghid-temei
„Persoanele fizice și juridice care au calitatea de angajatori sau sunt asimilate acestora [...] sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate."

*(Codul fiscal — Legea nr. 227/2015, art. 147 alin. (1), pentru D112 — una dintre cele 9 declarații urmărite lunar de semafor)*
:::

Fiecare dintre celelalte 8 declarații urmărite (D100, D101, D205, D300, D301, D390, D394, D406) are propriul termen și propria condiție de aplicabilitate — de aceea semaforul le evaluează individual, firmă cu firmă, nu după o singură regulă comună.

## Ce verifică, practic, semaforul în fiecare lună

Pentru firma selectată, semaforul evaluează simultan cele 9 declarații urmărite (D100, D101, D112, D205, D300, D301, D390, D394, D406) și arată, pentru fiecare, dacă e:
- **datorată și în termen** (verde),
- **cu termen apropiat, de urmărit** (galben, la ≤7 zile de scadență),
- **restantă** (roșu, termen deja depășit fără confirmare de depunere),
- **imposibil de evaluat** (gri, de regulă din lipsa unei informații din profilul firmei — regim fiscal, statut de TVA — necesară pentru a decide dacă declarația se aplică).

Fiecare verdict poartă motivul explicit — de exemplu, D112 apare doar în lunile în care firma a avut efectiv un salariat activ, iar D300/D394 apar doar dacă firma e înregistrată în scopuri de TVA.

## Ce se greșește în practică

- Se folosește o listă „standard" de declarații lunare, aceeași pentru toate firmele din portofoliu, fără să se țină cont că fiecare are propriul regim și propriul statut de TVA.
- Se ignoră starea „gri" ca fiind irelevantă — de fapt înseamnă că semaforul nu are destule date pentru firma respectivă, nu că nu există obligații de verificat.

## Ce face iConta.eu

Ecranul Control fiscal, alimentat de motorul F022 (`core/control_fiscal_api.py`), răspunde exact acestei întrebări pentru fiecare firmă: ce e datorat, cu ce termen, și de ce. Verdictul se recalculează la fiecare accesare, pe baza profilului fiscal curent al firmei și a declarațiilor deja confirmate ca depuse în aplicație.

[iConta.eu](/)
