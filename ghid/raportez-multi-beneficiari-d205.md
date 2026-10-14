---
title: "Cum raportez mai mulți beneficiari în D205"
description: "Cum sunt identificați, validați și incluși automat mai mulți beneficiari de dividende în aceeași declarație D205."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Cum raportez mai mulți beneficiari în D205

O declarație D205 poate conține oricâți beneficiari de dividende are firma, fiecare identificat prin CNP, cu bază de impozitare și impozit calculate individual.

Fiecare beneficiar apare ca înregistrare separată în XML, cu propriile câmpuri `divid_D`, `divid_P`, `baza1`, `imp1` și `cifR` (CNP). Suma de control din antetul declarației (`totalPlata_A`) agregă numărul de beneficiari, baza totală și impozitul total, calculate o singură dată la nivelul întregii declarații.

## Temeiul legal

::: ghid-temei
„(2) Plătitorii de venituri cu regim de reținere la sursă a impozitelor au obligația să depună o declarație privind calcularea și reținerea impozitului pentru fiecare beneficiar de venit la organul fiscal competent, până în ultima zi a lunii februarie inclusiv a anului curent pentru anul expirat [...]”
— Legea nr. 227/2015 privind Codul fiscal, art. 132 alin. (2) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„[...] se completează de către plătitorii de venituri din dividende, pentru fiecare persoană fizică beneficiară. Col. 1 - se completează pentru fiecare beneficiar de venit, înscriindu-se numele și prenumele persoanelor fizice. Col. 2 - se înscrie, pe fiecare beneficiar de venit, codul numeric personal sau numărul de identificare fiscală atribuit de către Agenția Națională de Administrare Fiscală cu ocazia înregistrării fiscale, după caz. [...] Col. 6 - se înscrie, pe fiecare beneficiar de venit, suma reprezentând totalul impozitului pe venit calculat și reținut în cursul anului.”
— OPANAF nr. 102/2025, anexa (anexa nr. 1 la OPANAF nr. 179/2022, instrucțiunile de completare a formularului 205), cap. II pct. 9 (sursă: [OPANAF nr. 102/2025 privind modificarea OPANAF nr. 179/2022 (formularele 205/207)](https://legislatie.just.ro/Public/DetaliiDocument/293917))
:::

## Ce se greșește în practică

Se introduc uneori manual beneficiari suplimentari fără a verifica dacă CNP-ul respectiv nu este deja prezent din altă sursă (de exemplu deja preluat automat din contul 457), ceea ce poate duce la duplicate respinse de validator.

## Ce face iConta.eu

„lista asociaților (Date firmă)” preia automat toți asociații cu cotă mai mare de zero și sumele lor din contul 457 (doar din note contabile validate), generând câte un beneficiar pentru fiecare. Validarea CNP se face pe cifră de control, nu doar prin verificarea că a fost completat, iar un CNP duplicat pentru același tip de venit (dividende) este blocat explicit înainte de generare. Suma de control `totalPlata_A` este calculată o singură dată din numărul de beneficiari, baza totală și impozitul total, și doar preluată (nu recalculată) în XML-ul final, pentru a evita neconcordanțe atunci când raportați mai mulți beneficiari în aceeași declarație.

[iConta.eu](/)
