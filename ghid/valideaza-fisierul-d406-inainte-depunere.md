---
title: Cum se validează fișierul D406 înainte de depunere?
description: Validarea D406 e un pas legal obligatoriu, cu validatorul oficial ANAF — explicăm procedura și cum e implementată tehnic.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se validează fișierul D406 înainte de depunere?

Depunerea D406 nu înseamnă doar generarea fișierului XML și trimiterea lui — procedura oficială prevede explicit un pas de validare, între generare și semnare/transmitere.

## Temeiul legal

::: ghid-temei
pct. 1-9 (procedură): generare XML → validare cu "Validator" (Soft J) → generare PDF cu XML atașat, semnat electronic → transmitere prin SPV sau e-guvernare.ro. — OPANAF nr. 1783/2021, Anexa 3.
:::

Ordinea pașilor prevăzută de lege este clară: (1) generarea fișierului XML, (2) validarea lui cu instrumentul oficial pus la dispoziție de ANAF ("Validator", cunoscut și ca Soft J), (3) generarea PDF-ului cu XML-ul atașat și semnarea electronică, (4) transmiterea prin Spațiul Privat Virtual (SPV) sau prin portalul e-guvernare.ro. Un fișier care nu trece pasul de validare nu ar trebui semnat și transmis ca atare.

## Ce se greșește în practică

Cea mai frecventă greșeală este sărirea pasului de validare — fie din grabă, fie din convingerea că "fișierul s-a generat, deci e corect". Generarea fără erori și validarea structurală/de conținut sunt lucruri diferite: fișierul poate fi bine format din punct de vedere XML și, în același timp, să conțină date care nu trec validarea specifică D406 (de exemplu conturi nemapate corect sau sume nereconciliate între antet și linii).

## Ce face iConta.eu

Validarea se face cu validatorul oficial `DUKIntegrator_AnLunaUI.jar`, integrat direct în aplicație (`core/duk.py`, funcția `valideaza(xml, tip, an=, luna=)`) — nu cu un validator generic sau propriu.

Un istoric tehnic relevant, pentru transparență: `DECIZII.md` (27.07.2026) documentează un bug reparat, în care butonul de validare D406 nu trimitea `an`/`luna` validatorului și întorcea mereu o stare neconcludentă ("GRI"), indiferent de conținutul real al fișierului. Bug-ul a fost corectat, iar validarea a fost confirmată cu rezultat „valid" pe date reale: tenant_002 (iunie 2026) și tenant_013 (2026-08).

Notă legată de conținutul fișierului validat: secțiunea SourceDocuments (facturi emise/primite) se generează cu linii reale per produs, reconciliate obligatoriu cu antetul, iar rezultatul e verificat structural prin DUK ("DUK-validate structural"). Secțiunea Payments rămâne, la acest moment, neemisă din lipsa unei surse de mapare a plăților din trezorerie (decizie de business în așteptare) — validarea reușește pe fișierul cu Payments gol, dar declarația nu conține date de plăți.

[iConta.eu](/)
