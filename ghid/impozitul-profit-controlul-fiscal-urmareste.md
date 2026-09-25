---
title: "Impozitul pe profit și controlul fiscal: ce urmărește inspectorul"
description: "Ce anume verifică inspecția fiscală, conform obiectului ei legal, la o firmă plătitoare de impozit pe profit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Impozitul pe profit și controlul fiscal: ce urmărește inspectorul

Obiectul unei inspecții fiscale nu e definit vag — Codul de procedură fiscală îl descrie punctual, iar la o firmă plătitoare de impozit pe profit, aceste puncte se concentrează pe corectitudinea bazei de impozitare și pe concordanța dintre declarații și evidența contabilă.

## Temeiul legal

::: ghid-temei
„Inspecția fiscală reprezintă activitatea ce are ca obiect verificarea legalității și conformității declarațiilor fiscale, corectitudinii și exactității îndeplinirii obligațiilor în legătură cu stabilirea obligațiilor fiscale de către contribuabil/plătitor, respectării prevederilor legislației fiscale și contabile, verificarea sau stabilirea, după caz, a bazelor de impozitare și a situațiilor de fapt aferente, stabilirea diferențelor de obligații fiscale principale."
— Legea 207/2015, art. 113 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce face concret organul de inspecție, potrivit alin. (2) al aceluiași articol:

- **Verifică concordanța** dintre datele din declarațiile fiscale și cele din evidența contabilă și fiscală, „inclusiv din fișierul standard de control fiscal" (SAF-T) — pentru impozitul pe profit, asta înseamnă compararea D101 cu balanța și cu jurnalele de venituri/cheltuieli.
- **Analizează și confruntă** declarațiile cu informații proprii sau din alte surse, în căutarea unor elemente noi relevante — inclusiv date de la terți (furnizori, clienți, bănci).
- **Stabilește baza de impozitare** și diferențele față de ce a declarat contribuabilul, atunci când constată neconcordanțe.
- **Solicită explicații scrise** reprezentantului legal ori de câte ori sunt necesare pentru clarificarea constatărilor.

## Ce se greșește în practică

- Se pregătește dosarul de control doar cu declarațiile depuse, fără evidența contabilă și fiscală completă care să le susțină — inspecția verifică explicit concordanța dintre cele două, nu doar declarația izolată.
- Se răspunde verbal la solicitările de clarificare din timpul controlului, fără să se păstreze o copie scrisă a explicațiilor date — art. 113 alin. (2) lit. g) prevede explicații scrise, utile ulterior la o eventuală contestație.
- Se presupune că inspecția verifică doar perioada menționată explicit „pe hârtie" în aviz, ignorând că raportul de inspecție cuprinde constatări pentru toate obligațiile fiscale înscrise în avizul de inspecție, plus alte obligații prevăzute de legislația fiscală și contabilă ce au făcut obiectul verificării.

## Ce face iConta.eu

iConta.eu are un motor de control fiscal încrucișat (`core/control_incrucisat.py`, coordonat prin `core/control_fiscal_api.py`) care verifică independent concordanța dintre TVA, D112 (salarii) și D390 (intracomunitar) cu datele din evidența contabilă a firmei — aceleași tipuri de neconcordanțe pe care le urmărește și inspecția fiscală, potrivit art. 113 alin. (2) lit. b). Aplicația semnalează constatările „roșii" printr-un sistem de alerte (`core/alerte_control_fiscal.py`), agregat pe firmă, pentru ca acestea să fie corectate înainte de un eventual control real — dar nu simulează sau nu înlocuiește inspecția fiscală propriu-zisă, care rămâne o procedură administrativă separată.

[iConta.eu](/)
