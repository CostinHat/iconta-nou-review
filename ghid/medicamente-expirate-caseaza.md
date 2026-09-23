---
title: "Medicamente expirate: cum se casează"
description: Medicamentele cu termen de valabilitate depășit sunt deductibile explicit la impozitul pe profit, dar operația corectă în evidența contabilă e „Minus" (lipsă neimputabilă de stoc), nu „Casare" — aceasta din urmă e rezervată mijloacelor fixe.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Medicamente expirate: cum se casează

Termenul „casare" se folosește în practică și pentru scoaterea din gestiune a medicamentelor expirate, dar contabil e vorba de o lipsă de stoc neimputabilă, nu de o casare de mijloc fix. Vestea bună: legea prevede explicit deductibilitatea acestei cheltuieli, spre deosebire de alte lipsuri de marfă.

## Temeiul legal

::: ghid-temei
„cheltuielile privind bunurile de natura stocurilor [...] constatate lipsă din gestiune ori degradate, neimputabile [...] sunt deductibile în următoarele situații/condiții: [...] 7. alte bunuri [...] dacă termenul de valabilitate/expirare este depășit, potrivit legii."
— Codul fiscal, art. 25 alin. (4) lit. c) pct. 7
:::

::: ghid-temei
„Nu se ajustează deducerea inițială a taxei în cazul: a) bunurilor distruse, pierdute sau furate, în condițiile în care aceste situații sunt demonstrate sau confirmate în mod corespunzător de persoana impozabilă."
— Codul fiscal, art. 304 alin. (2) lit. a)
:::

Spre deosebire de o marfă pur și simplu pierdută sau degradată fără explicație, medicamentele expirate au un temei de deductibilitate explicit la impozitul pe profit — punctul 7 din lista limitativă a art. 25 alin. (4) lit. c) acoperă exact „termenul de valabilitate/expirare [...] depășit, potrivit legii". Cât despre TVA, dedusă inițial la achiziție, ea nu se ajustează dacă distrugerea medicamentelor expirate e demonstrată sau confirmată corespunzător (de exemplu printr-un proces-verbal de distrugere, conform procedurii legale aplicabile domeniului farmaceutic) — dacă nu există o asemenea dovadă, ajustarea TVA rămâne obligatorie.

## Ce se greșește în practică

- Se caută în aplicație operația „Casare" pentru medicamente, pentru că așa se numește colocvial procesul — dar „Casare" e rezervată, în evidența contabilă, mijloacelor fixe; medicamentele, fiind stoc, se scad din gestiune prin operația „Minus".
- Se presupune că orice medicament expirat e automat deductibil fiscal, fără să existe dovada distrugerii/procedura legală aplicabilă — deductibilitatea la pct. 7 e condiționată de faptul că expirarea e tratată „potrivit legii", nu doar constatată.
- Se omite ajustarea TVA atunci când nu există dovadă de distrugere corespunzătoare.

## Ce face iConta.eu

Pentru scoaterea din gestiune a medicamentelor expirate, operația relevantă e „Minus" din formularul „Inventariere anuală" — nu „Casare", care în aplicație e rezervată exclusiv mijloacelor fixe (identificate printr-un `mijloc_fix_id` din registrul de mijloace fixe) și nu acceptă conturi de stoc. La „Minus", marchezi lipsa ca neimputabilă; cota de TVA e obligatorie, fără valoare implicită. Dacă bifezi că lipsa e „asigurată sau distrusă dovedit", aplicația nu adaugă linia de ajustare TVA; altfel, o generează automat. Evaluarea dacă medicamentele respective se încadrează efectiv la pct. 7 (deductibilitate) rămâne o decizie a ta, pe baza documentelor de distrugere — aplicația nu face această verificare automat.

[iConta.eu](/)
