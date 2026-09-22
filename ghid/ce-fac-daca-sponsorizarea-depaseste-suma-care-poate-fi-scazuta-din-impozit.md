---
title: Ce fac dacă sponsorizarea depășește suma care poate fi scăzută din impozit?
description: La impozitul pe profit, azi (regim din 03.02.2022) suma care depășește plafonul de min(0,75% din cifra de afaceri; 20% din impozitul pe profit) nu se pierde definitiv doar dacă rămâne loc de redirecționare prin D177 până la termenul D101; dacă sponsorizarea efectivă a atins deja plafonul, excedentul propriu-zis rămâne cheltuială nedeductibilă.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce fac dacă sponsorizarea depășește suma care poate fi scăzută din impozit?

Legea limitează suma pe care o puteți scădea din impozitul pe profit pentru sponsorizări — nu tot ce donați se transformă automat în credit fiscal. Când suma sponsorizată depășește acest plafon, e important să știți exact ce se întâmplă cu diferența.

## Temeiul legal

::: ghid-temei
„i) cheltuielile de sponsorizare și/sau mecenat, acordate potrivit legii; contribuabilii care efectuează sponsorizări și/sau acte de mecenat, potrivit prevederilor Legii nr. 32/1994 privind sponsorizarea, cu modificările și completările ulterioare, și ale Legii bibliotecilor nr. 334/2002, republicată, cu modificările și completările ulterioare, scad sumele aferente din impozitul pe profit datorat la nivelul valorii minime dintre următoarele:
1. valoarea calculată prin aplicarea a 0,75% la cifra de afaceri; pentru situațiile în care reglementările contabile aplicabile nu definesc indicatorul cifra de afaceri, această limită se determină potrivit normelor;
2. valoarea reprezentând 20% din impozitul pe profit datorat. În cazul sponsorizărilor efectuate către entități persoane juridice fără scop lucrativ, inclusiv unități de cult, sumele aferente acestora se scad din impozitul pe profit datorat, în limitele prevăzute de prezenta literă, doar dacă beneficiarul sponsorizării este înscris, la data încheierii contractului, în Registrul entităților/unităților de cult pentru care se acordă deduceri fiscale, potrivit alin. (4^1).”

— *Codul fiscal, art. 25 alin. (4) lit. i), forma actuală.*

„2. (1) Valoarea impozitului pe profit sau a diferenţei de impozit pe profit care poate fi redirecţionată se calculează prin scăderea din valoarea minimă stabilită, potrivit art. 25 alin. (4) lit. i) din Legea nr. 227/2015 privind Codul fiscal..., a sumelor reprezentând sponsorizare şi/sau mecenat, acordate entităţilor beneficiare în anul pentru care s-a depus declaraţia anuală de impozit pe profit, ..., şi a sumelor reportate, astfel cum au fost înscrise în formularul 101 «Declaraţie privind impozitul pe profit» a anului respectiv.”

„1. Plătitorii de impozit pe profit pot dispune redirecţionarea unor sume din impozitul datorat, potrivit legii, până la termenele legale de depunere a declaraţiei anuale de impozit pe profit [D101].”

— *OPANAF nr. 3562/2024, procedura D177.*
:::

## Ce se întâmplă cu suma peste plafon

Plafonul deductibil este `min(0,75% × cifra de afaceri, 20% × impozitul pe profit datorat)`. Aici trebuie făcută o distincție importantă:

- Dacă **sponsorizarea efectivă acordată** este mai mare decât acest plafon, creditul fiscal se oprește la nivelul plafonului — restul rămâne, pur și simplu, o cheltuială care nu poate fi scăzută din impozitul pe profit pe această cale. Nu există un mecanism legal de reportare sau redirecționare pentru excedentul propriu-zis din regimul actual (spre deosebire de regimul dinainte de 03.02.2022, când exista reportare pe 7 ani — vezi mai jos).
- Dacă, în schimb, sponsorizarea efectivă acordată este **mai mică** decât plafonul, firma are „spațiu” neconsumat până la plafon — și îl poate folosi separat, prin formularul D177, redirecționând direct din impozitul pe profit datorat o sumă suplimentară către entități eligibile, fără să fi acordat efectiv acea sumă sub formă de sponsorizare contractuală. Această redirecționare se face până la termenul legal de depunere a D101 pentru anul respectiv.

::: ghid-exemplu
O firmă cu cifra de afaceri 5.000.000 lei și impozit pe profit datorat 40.000 lei are un plafon de `min(0,75% × 5.000.000; 20% × 40.000) = min(37.500; 8.000) = 8.000 lei`. Dacă firma a sponsorizat efectiv 12.000 lei, creditul se oprește la 8.000 lei; cei 4.000 lei în plus rămân o cheltuială nedeductibilă pentru calculul acestui credit, fără posibilitate de reportare sau redirecționare suplimentară. Dacă, în schimb, firma a sponsorizat efectiv doar 5.000 lei, mai are 3.000 lei „spațiu” neconsumat din plafon, pe care îl poate redirecționa direct prin D177, până la termenul de depunere a D101.
:::

**Atenție dacă verificați o sponsorizare dintr-un an anterior lui 2022:** pentru sponsorizările acordate până la 02.02.2022, plafonul era 0,5% din cifra de afaceri (nu 0,75%), iar excedentul peste plafon nu se pierdea, ci se **reporta pe 7 ani consecutivi** — mecanismul D177 nu exista atunci. Pentru astfel de ani, nu aplicați regula descrisă mai sus.

## Ce se greșește în practică

- Se crede că suma peste plafon se pierde definitiv indiferent de situație, fără a verifica dacă mai există spațiu de redirecționare prin D177 (relevant doar când sponsorizarea efectivă e sub plafon, nu peste el).
- Se calculează plafonul folosind un singur criteriu (doar cifra de afaceri sau doar impozitul pe profit), în loc de a lua minimul dintre cele două.
- Se omite verificarea Registrului entităților/unităților de cult: dacă beneficiarul nu era înscris la data încheierii contractului, tot creditul e nedatorat, nu doar excedentul.
- Se depune D177 după termenul legal de depunere a D101 a anului respectiv, pierzând posibilitatea de redirecționare.
- Se aplică regula actuală (0,75%, D177) unei sponsorizări dintr-un an anterior lui 2022, unde regula era 0,5% cu reportare pe 7 ani.

## Ce face iConta.eu

În `core/sponsorizari.py`, `plafon_credit()` calculează `min(0,75% × cifra de afaceri, 20% × impozit pe profit)`, iar `credit_sponsorizare()` calculează `credit = min(sponsorizari_efectuate, plafon)` și `redirectionabil_d177 = plafon - credit`. Așadar, când sponsorizarea depășește plafonul, `credit` este limitat la valoarea plafonului, iar `redirectionabil_d177` iese 0 — nu mai există spațiu suplimentar de redirecționare, iar diferența dintre sponsorizarea efectivă și plafon rămâne, corect, în afara calculului.

Rețineți însă: motorul aplică această regulă (0,75%/D177) **indiferent de `la_data` transmisă**, chiar și pentru ani anteriori lui 2022, când legea prevedea altceva (0,5% cu reportare pe 7 ani). Pentru sponsorizări din 2019–2021, nu vă bazați pe rezultatul automat.

[iConta.eu](/)
