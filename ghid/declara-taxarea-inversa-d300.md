---
title: "Cum se declară taxarea inversă în D300"
description: Taxarea inversă apare în D300 pe două rânduri, în funcție de rol — furnizorul declară doar baza, fără TVA (rândul 13), iar beneficiarul autolichidează TVA-ul pe cont propriu, cu efect net zero (rândurile 12 + 26).
published: 2026-09-25
modified: 2026-10-13
poarta: v1
---

# Cum se declară taxarea inversă în D300

La taxarea inversă, TVA nu circulă între furnizor și beneficiar — furnizorul emite factura fără TVA, iar beneficiarul e cel care calculează și înregistrează TVA-ul, atât ca taxă colectată, cât și ca taxă deductibilă, în același decont. Efectul pentru beneficiar e net zero, dar tranzacția tot trebuie să apară în D300.

## Temeiul legal

::: ghid-temei
**Art. 323 alin. (1) Cod fiscal (Legea 227/2015):** *„... trebuie să depună ... un decont de taxă, până la data de 25 inclusiv a lunii următoare celei în care se încheie perioada fiscală respectivă."*

„Rândul 13 - se înscriu informaţiile preluate din jurnalul de vânzări*) privind baza de impozitare pentru livrările/prestările efectuate, pentru care furnizorii/prestatorii aplică măsurile de simplificare prevăzute la art. 331 din Codul fiscal, pentru operaţiuni a căror exigibilitate intervine în perioada de raportare sau în perioade fiscale anterioare.”
— OPANAF 174/2026, anexa 2, instrucțiunile de completare a formularului 300, rândul 13 (sursă: [OPANAF nr. 174/2026 pentru aprobarea formularului 300 (Decont de TVA)](https://legislatie.just.ro/Public/DetaliiDocument/307258))

„Rândul 12 - se înscriu informaţiile preluate din jurnalul de cumpărări*) privind baza de impozitare şi taxa colectată pentru achiziţiile de bunuri şi de servicii, a căror exigibilitate intervine în perioada de raportare, de către beneficiarii care aplică măsurile de simplificare prevăzute la art. 331 din Codul fiscal.”
— OPANAF 174/2026, anexa 2, instrucțiunile de completare a formularului 300, rândul 12 (sursă: [OPANAF nr. 174/2026 pentru aprobarea formularului 300 (Decont de TVA)](https://legislatie.just.ro/Public/DetaliiDocument/307258))

„Rândul 26 - se înscriu informaţiile preluate din jurnalul de cumpărări*) privind baza de impozitare şi taxa deductibilă pentru achiziţiile de bunuri şi de servicii, a căror exigibilitate intervine în perioada de raportare, de către beneficiarii care aplică măsurile de simplificare prevăzute la art. 331 din Codul fiscal.”
— OPANAF 174/2026, anexa 2, instrucțiunile de completare a formularului 300, rândul 26 (sursă: [OPANAF nr. 174/2026 pentru aprobarea formularului 300 (Decont de TVA)](https://legislatie.just.ro/Public/DetaliiDocument/307258))
:::

## Cum apare taxarea inversă în decont

Potrivit instrucțiunilor de completare a formularului 300:

- **Pentru furnizor** — livrarea apare pe rândul **13**, cu baza de impozitare, fără TVA. Furnizorul nu colectează și nu declară TVA pentru această operațiune.
- **Pentru beneficiar** — achiziția apare pe rândurile **12 (taxă colectată prin autolichidare) + 26 (taxă dedusă)**, cu efect net zero asupra sumei de plată, dar cu obligația de a raporta ambele rânduri, nu doar unul.

Efectul „net zero" nu înseamnă că operațiunea nu se declară — înseamnă că suma de TVA colectată prin autolichidare se anulează cu suma dedusă, în același decont, dar ambele rânduri trebuie completate corect pentru ca decontul să reflecte tranzacția.

## Ce se greșește în practică

- **Se omite complet operațiunea din decont**, pe motiv că „nu e TVA de plată" — chiar cu efect net zero, operațiunea trebuie raportată pe rândurile corespunzătoare (rândul 13 la furnizor, rândurile 12 + 26 la beneficiar).
- **Beneficiarul completează doar taxa dedusă (rândul 26), fără taxa colectată prin autolichidare (rândul 12)** — taxarea inversă cere ambele înregistrări, nu doar deducerea.
- **Se aplică taxare inversă pe operațiuni care nu se încadrează la art. 331** — regimul e specific anumitor categorii de bunuri/servicii, nu o opțiune generală a părților.

## Ce face iConta.eu

Decontul de TVA v12 rutează automat operațiunile de taxare inversă pe rândurile corecte — rândul 13 pentru furnizor, rândurile 12 + 26 pentru beneficiar — pe baza clasificării operațiunii introduse în aplicație. Rândurile manuale pentru taxare inversă, intracomunitar și regularizări se introduc și se editează dintr-un panou dedicat, cu buton „Regenerează D300" după fiecare modificare.

[iConta.eu](/)
