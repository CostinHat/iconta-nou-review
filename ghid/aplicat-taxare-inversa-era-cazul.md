---
title: Am aplicat taxare inversă unde nu era cazul
description: Dacă operațiunea nu se încadrează la art. 331 (categorie greșită, un partener neînregistrat în scopuri de TVA, categorie expirată sau sub prag), factura trebuia să aibă TVA normal — corectarea înseamnă stornarea facturii greșite și reemiterea ei cu TVA.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Am aplicat taxare inversă unde nu era cazul

Taxarea inversă de la art. 331 CF nu e o opțiune la alegere — se aplică doar dacă operațiunea îndeplinește, cumulativ, toate condițiile din lege. Dacă una lipsește, factura trebuia emisă cu TVA normal, iar aplicarea greșită a taxării inverse trebuie corectată.

## Temeiul legal

::: ghid-temei
„Condiția obligatorie pentru aplicarea taxării inverse este ca atât furnizorul, cât și beneficiarul să fie înregistrați în scopuri de TVA conform art. 316."
— Legea 227/2015, art. 331 alin. (1)
:::

::: ghid-temei
„Prevederile alin. (2) lit. c)-f) și i)-l) se aplică până la data de 31 decembrie 2026 inclusiv."
— Legea 227/2015, art. 331 alin. (6)
:::

Verifică, în ordine, care condiție nu a fost de fapt îndeplinită:
1. **Categoria** operațiunii nu se regăsește, de fapt, la art. 331 alin. (2) — de exemplu, ai facturat invers o lucrare de construcție, nu vânzarea unei clădiri/teren taxabil (singura situație imobiliară acoperită, lit. g).
2. **Unul din parteneri nu era înregistrat în scopuri de TVA** la data operațiunii (art. 331 alin. (1)).
3. **Categoria expirase** deja (majoritatea categoriilor expiră la 31.12.2026, potrivit art. 331 alin. (6)) sau nu se atinsese pragul valoric de 22.500 lei, acolo unde se aplică (telefoane, circuite integrate, console/tablete/laptopuri, art. 331 alin. (7)).

O dată identificată cauza, corecția presupune stornarea facturii emise eronat fără TVA și reemiterea ei cu TVA normal, la cota aplicabilă operațiunii, cu ajustarea corespunzătoare în decontul de TVA din perioada afectată (sau, dacă decontul a fost deja depus, printr-o declarație rectificativă). **Sursele verificate pentru acest ghid** confirmă condițiile de fond de mai sus și consecința opusă (aplicarea greșită a TVA în loc de taxare inversă, cu pierderea dreptului de deducere la beneficiar, norme pct. 109 alin. (4)) — nu au identificat însă un text normativ distinct, dedicat exact situației inverse (taxare inversă aplicată eronat, unde ar fi trebuit TVA normal); corectarea descrisă mai sus urmează principiul general de rectificare a unei facturi întocmite greșit, nu un articol specific citat separat pentru acest caz.

## Ce se greșește în practică

- Se aplică taxare inversă „din prudență" oricărui partener plătitor de TVA, fără verificarea prealabilă a categoriei exacte de la art. 331 alin. (2).
- Se ignoră expirarea unei categorii (31.12.2026 pentru majoritatea) sau pragul valoric, continuând să se aplice taxare inversă după ce condiția nu mai era îndeplinită.
- Se corectează doar ulterior nota contabilă internă, fără să se emită și o factură corectată către partener, deși taxa de pe factură e cea care contează pentru deducerea beneficiarului.

## Ce face iConta.eu

Motorul de taxare inversă al iConta.eu (`se_aplica`) verifică, la fiecare operațiune, categoria, înregistrarea în scopuri de TVA a ambelor părți, expirarea și pragul valoric — și respinge explicit operațiunea, cu mesaj de eroare, dacă vreo condiție nu e îndeplinită. Dacă ai aplicat totuși taxare inversă manual, în afara acestei validări (de exemplu direct pe factură, fără să treci prin ecranul dedicat), aplicația nu poate detecta retroactiv greșeala — corectarea (stornarea și reemiterea facturii, plus ajustarea decontului) rămâne un pas manual, de făcut direct de tine.

[iConta.eu](/)
