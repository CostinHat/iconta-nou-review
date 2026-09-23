---
title: "Cum raportez mai mulți beneficiari în D205"
description: "Cum sunt identificați, validați și incluși automat mai mulți beneficiari de dividende în aceeași declarație D205."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum raportez mai mulți beneficiari în D205

O declarație D205 poate conține oricâți beneficiari de dividende are firma, fiecare identificat prin CNP, cu bază de impozitare și impozit calculate individual.

## Temeiul legal

::: ghid-temei
"CUI plătitor și CNP fiecărui beneficiar sunt pre-validate pe cifră de control (checksum), nu doar pe «non-gol»; un CNP duplicat pe cheia (tip_venit+CNP) e blocat explicit" — regulă DUK R41b.
— comportament al generatorului D205, `core/d205.py:180-236, 238-250`
:::

Fiecare beneficiar apare ca înregistrare separată în XML, cu propriile câmpuri `divid_D`, `divid_P`, `baza1`, `imp1` și `cifR` (CNP). Suma de control din antetul declarației (`totalPlata_A`) agregă numărul de beneficiari, baza totală și impozitul total, calculate o singură dată la nivelul întregii declarații.

## Ce se greșește în practică

Se introduc uneori manual beneficiari suplimentari fără a verifica dacă CNP-ul respectiv nu este deja prezent din altă sursă (de exemplu deja preluat automat din contul 457), ceea ce poate duce la duplicate respinse de validator.

## Ce face iConta.eu

`select_asociati` (`core/repo_d205.py`) preia automat toți asociații cu cotă mai mare de zero și sumele lor din contul 457 (doar din note contabile validate), generând câte un beneficiar pentru fiecare. Validarea CNP se face pe cifră de control, nu doar prin verificarea că a fost completat, iar un CNP duplicat pentru același tip de venit (dividende) este blocat explicit înainte de generare. Suma de control `totalPlata_A` este calculată o singură dată din numărul de beneficiari, baza totală și impozitul total, și doar preluată (nu recalculată) în XML-ul final, pentru a evita neconcordanțe atunci când raportați mai mulți beneficiari în aceeași declarație.

[iConta.eu](/)
