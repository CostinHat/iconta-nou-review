---
title: "Cum se depune o declarație rectificativă pentru impozitul micro?"
description: "Fluxul legal și practic pentru corectarea unei declarații D100 pe impozitul pe veniturile microîntreprinderilor (cod 121), prin declarația 710."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se depune o declarație rectificativă pentru impozitul micro?

Dacă ai declarat greșit impozitul pe veniturile microîntreprinderilor prin formularul 100 — sumă greșită, cotă greșită, o eroare de calcul — corecția nu se face printr-un nou D100, ci printr-o **declarație rectificativă, formularul 710**. Pentru impozitul micro (cod de obligație 121), formularul are o particularitate importantă: cota de impozitare trebuie completată obligatoriu, iar la ultimul trimestru scadența e diferită de restul anului.

## Temeiul legal

::: ghid-temei
„Anexa nr. 5 INSTRUCȚIUNI de completare a formularului 710 «Declarație rectificativă», cod 14.13.01.00/r [...] Capitolul I. Depunerea declarației. Declarația rectificativă se utilizează pentru corectarea impozitelor și taxelor administrate de Agenția Națională de Administrare Fiscală și stabilite de către plătitori prin autoimpunere sau cu regim de reținere la sursă, declarate în formularul 100 «Declarație privind obligațiile de plată la bugetul de stat»."
— OPANAF 587/2016, Anexa 5, Cap. I (sursă: anaf_surse/opanaf_587_2016_aprobarea_modelului_continutului_formularelor_utilizate.txt)
:::

- Formularul 710 nu e o declarație de sine stătătoare pentru orice obligație — corectează exclusiv sume declarate deja prin D100, prin autoimpunere sau reținere la sursă.
- Coloanele formularului sunt „Suma inițială" și „Suma corectată": „Coloana «Suma inițială»: [...] se completează [...] înscriindu-se suma care s-a completat eronat în declarația care se rectifică [...]. Coloana «Suma corectată»: [...] se completează [...] înscriindu-se suma corectă reprezentând impozitul sau taxa datorat/datorată în perioada la care se referă declarația corectată" (aceeași sursă, Anexa 5 pct. 3).
- Rectificativa nu poate fi depusă oricând: „Declarația nu poate fi depusă după anularea rezervei verificării ulterioare", cu excepții stricte — corecție impusă de o condiție legală ulterioară, sau o hotărâre judecătorească definitivă (aceeași sursă, Anexa 5, Cap. I). Aceleași excepții sunt confirmate la nivel de lege, verbatim: „(5) Declarația de impunere nu poate fi depusă și nu poate fi corectată după anularea rezervei verificării ulterioare. (6) Prin excepție [...] a) în situația în care corecția se datorează îndeplinirii sau neîndeplinirii unei condiții prevăzute de lege [...]" — CPF (Legea 207/2015), art. 105 alin. (5)-(6).

## Ce se greșește în practică

- Se încearcă redepunerea unui D100 „corect" pentru aceeași perioadă, în loc de o declarație 710 — D100 nu are un mecanism intern de rectificare, corecția lui trece prin 710.
- Se completează doar suma corectă, fără suma inițială declarată greșit — formularul cere ambele coloane, pentru ca ANAF să poată calcula diferența.
- Se uită cota de impozitare la corecțiile pe impozit micro (cod 121) — la acest cod cota e obligatorie pe rectificativă, spre deosebire de impozitul pe profit (cod 103), unde nu se completează.
- Se calculează scadența rectificativei ca și cum ar fi identică tot anul — pentru trimestrul IV la impozitul micro, termenul e special (vezi mai jos).

## Ce face iConta.eu

iConta.eu generează efectiv formularul 710 pentru cod de obligație 121 (impozit micro), din ecranul **Declarații** → tip D710 → perioadă (trimestru) → panoul „Obligații corectate": se alege codul 121, se completează suma declarată inițial, suma corectă și cota de impozitare (câmpul de cotă apare automat doar la acest cod). Declarația e trecută prin validatorul oficial ANAF (DUK) înainte de a fi considerată validă, iar aplicația blochează explicit cazurile clar greșite — cotă lipsă la cod 121, CUI invalid, sume negative sau declarație goală — cu mesaj de eroare, nu cu o excepție tehnică. Pentru trimestrul IV, aplicația calculează automat scadența specială (25 iunie anul următor, în loc de 25 ianuarie).

O limitare reală, verificată în cod: motorul suportă și o **deducere** (`suma_ded`) la corecțiile pe cod 121, dar formularul din ecranul Declarații **nu are încă un câmp pentru ea** — doar cod, sumă inițială, sumă corectă și cotă. Dacă rectificativa ta implică o deducere, ea nu poate fi introdusă azi direct din formularul vizibil.

De asemenea, iConta.eu **nu depune automat** declarația la ANAF/SPV și nu confirmă automat că rectificativa a înlocuit declarația inițială — generează XML-ul validat; depunerea efectivă în portalul SPV rămâne un pas separat, făcut de contabil.

[iConta.eu](/)
