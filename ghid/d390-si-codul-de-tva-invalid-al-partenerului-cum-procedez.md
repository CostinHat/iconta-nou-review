---
title: D390 și codul de TVA invalid al partenerului — cum procedez?
description: Aplicația raportează operațiunea chiar dacă validarea VIES eșuează (avertisment, nu blocare), dar un cod de TVA invalid sau incorect declarat poate anula scutirea de TVA pentru livrarea intracomunitară respectivă, conform art. 294 alin. (2^1) din Codul fiscal.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# D390 și codul de TVA invalid al partenerului — cum procedez?

Când introduci o livrare sau achiziție intracomunitară cu un partener al cărui cod de TVA nu trece validarea VIES, aplicația nu blochează operațiunea — dar asta nu înseamnă că problema e minoră. Mai jos, ce face aplicația și de ce miza fiscală e mai mare decât pare la prima vedere.

## Temeiul legal

::: ghid-temei
**Art. 294 alin. (2) lit. a)**: „Sunt, de asemenea, scutite de taxă următoarele: a) livrările intracomunitare de bunuri către o persoană impozabilă sau către o persoană juridică neimpozabilă care acționează ca atare în alt stat membru decât cel în care începe expedierea sau transportul bunurilor, care îi comunică furnizorului un cod valabil de înregistrare în scopuri de TVA, atribuit de autoritățile fiscale din alt stat membru [...]"

**Art. 294 alin. (2^1)**: „Scutirea prevăzută la alin. (2) lit. a) nu se aplică în cazul în care furnizorul nu a respectat obligația prevăzută la art. 325 alin. (1) de a depune o declarație recapitulativă sau declarația recapitulativă depusă de acesta nu conține informațiile corecte referitoare la această livrare, astfel cum se solicită în temeiul art. 325 alin. (3), cu excepția cazului în care furnizorul poate justifica în mod corespunzător deficiența într-un mod considerat satisfăcător de autoritățile fiscale competente."
:::

## De ce nu e doar o formalitate

Codul valabil de TVA al cumpărătorului dintr-un alt stat membru nu e un simplu câmp de completat pe factură — e chiar una dintre condițiile de fond ale scutirii de TVA pentru livrarea intracomunitară (art. 294 alin. (2) lit. a)). Iar din 2020 (prin introducerea alin. (2^1)), legea leagă explicit scutirea de corectitudinea D390: dacă declarația recapitulativă lipsește sau conține informații greșite despre livrare, furnizorul riscă să piardă scutirea — deci să datoreze TVA colectat suplimentar pe operațiunea respectivă, nu doar să primească o solicitare de corectare de la ANAF.

Cu alte cuvinte, un cod de TVA invalid raportat greșit în D390 nu e doar un risc de respingere a declarației — e un risc de TVA suplimentar de plată, dacă situația nu se corectează la timp și în mod justificat.

## Ce se greșește în practică

- Se ignoră avertismentul de checksum VIES pentru că declarația se generează oricum, fără să se mai verifice ulterior codul real al partenerului.
- Se presupune că validarea VIES la momentul facturării e suficientă și nu se reverifică periodic, deși un cod poate deveni invalid ulterior (radiere, suspendare).
- Nu se păstrează dovada verificării VIES (captură, jurnal) care ar putea servi ca justificare „satisfăcătoare" în fața organului fiscal, conform excepției din art. 294 alin. (2^1).
- Se corectează codul de TVA direct în evidență, fără să se depună și o D390 rectificativă pentru perioada în care operațiunea a fost raportată inițial greșit.

## Ce face iConta.eu

Validarea checksum-ului VIES (`checksum_vies`) este implementată ca **avertisment, nu ca blocare**: o operațiune cu un cod de TVA care nu trece validarea structurală se raportează totuși în D390, cu avertisment explicit către contabil. Decizia de produs a fost motivată astfel: o operațiune obligatorie raportată cu un cod de TVA invalid e mai bună decât una care dispare tăcut din declarație.

Această alegere tehnică nu elimină însă obligația contabilului de a verifica și corecta codul de TVA al partenerului înainte de depunerea finală — miza nu e validarea structurii XML, ci păstrarea scutirii de TVA pentru livrarea respectivă, conform art. 294 alin. (2^1).

[iConta.eu](/)
