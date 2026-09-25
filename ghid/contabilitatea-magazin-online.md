---
title: "Cum se ține contabilitatea unui magazin online"
description: "Contabilitatea unui magazin online urmează regulile generale de comerț cu amănuntul; elementul specific real e pragul de 10.000 euro pentru vânzările intracomunitare la distanță, conform Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se ține contabilitatea unui magazin online

Nu există un regim contabil separat, dedicat "magazinelor online" — un magazin online e, din punct de vedere contabil și fiscal, o activitate de comerț (vânzare de bunuri), supusă acelorași reguli generale ca orice alt comerciant. Diferența reală apare atunci când magazinul vinde către clienți persoane fizice din alte state membre UE: aici intervine un prag legal precis, care schimbă unde se datorează TVA.

## Temeiul legal

::: ghid-temei
„(1) Prevederile art. 275 alin. (2) si art. 278 alin. (5) lit. h) nu se aplică dacă sunt îndeplinite cumulativ următoarele condiții: a) furnizorul sau prestatorul este stabilit [...] într-un singur stat membru; b) [...] sunt expediate ori transportate bunuri către un stat membru, altul decât statul membru prevăzut la lit. a); și c) valoarea totală, fără TVA, a operațiunilor prevăzute la lit. b) nu depășește, în anul calendaristic curent, 10.000 euro sau echivalentul acestei sume în moneda națională și nici nu a depășit această sumă în cursul anului calendaristic precedent.
(2) Atunci când, în cursul unui an calendaristic, pragul prevăzut la alin. (1) lit. c) este depășit, prevederile art. 275 alin. (2) și art. 278 alin. (5) lit. h) se aplică de la momentul depășirii pragului."
— Legea 227/2015, art. 278^1 alin. (1)-(2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce trebuie să înțeleagă concret un magazin online:

- Pentru **vânzările din România către clienți din România**, contabilitatea nu diferă cu nimic de un magazin fizic — venituri din vânzarea mărfurilor (cont 707), TVA colectată la cota aplicabilă bunului vândut, descărcare de gestiune (607/371), la fel ca orice comerciant.
- Pentru **vânzările intracomunitare la distanță** (bunuri expediate către persoane neimpozabile din alt stat membru UE), cât timp valoarea lor cumulată nu depășește **10.000 euro pe an calendaristic** (plafon comun cu serviciile electronice/telecom furnizate persoanelor neimpozabile din alte state membre), TVA se colectează tot la cota din România.
- Odată **depășit pragul de 10.000 euro** în cursul anului, de la momentul depășirii, locul livrării se consideră a fi statul membru de destinație — firma trebuie fie să se înregistreze în scopuri de TVA în fiecare stat membru relevant, fie să opteze pentru regimul special OSS (One Stop Shop), care permite declararea centralizată a TVA datorate în toate statele membre printr-o singură declarație depusă la ANAF.
- Firma poate opta și voluntar pentru aplicarea regulilor de la art. 275 alin. (2)/art. 278 alin. (5) lit. h) chiar înainte de a depăși pragul, opțiune valabilă pentru minimum doi ani calendaristici (art. 278^1 alin. (3)).

## Ce se greșește în practică

- Se aplică TVA românească la toate vânzările către clienți din UE, indiferent de sumă, ignorând că după depășirea pragului de 10.000 euro TVA se datorează în statul de destinație.
- Se calculează pragul de 10.000 euro doar din vânzările de bunuri la distanță, fără a-l cumula cu eventualele venituri din servicii electronice/telecomunicații furnizate persoanelor neimpozabile din alte state membre — plafonul e comun pentru ambele categorii.
- Se caută, fără rezultat, un set de reguli contabile "speciale pentru e-commerce" pentru operațiuni pur interne (vânzări în România) — pentru acestea, regulile generale de comerț cu amănuntul se aplică neschimbate.

## Ce face iConta.eu

iConta.eu ține evidența vânzărilor de mărfuri, a TVA colectate și a descărcării de gestiune la fel indiferent de canalul de vânzare (fizic sau online). Aplicația are un modul dedicat pentru declarația specială de TVA pentru regimurile speciale OSS/IOSS (D398, `core/d398.py`), dar acesta e declarativ: nu ține evidența automată a operațiunilor OSS pe stat de consum și cotă străină, așa că sumele pe fiecare stat membru se introduc manual. La data acestui ghid, aplicația nu urmărește automat cumulul anual al vânzărilor intracomunitare la distanță față de pragul de 10.000 euro de la art. 278^1 — verificarea depășirii pragului și, dacă e cazul, opțiunea pentru OSS rămân responsabilitatea contabilului.

[iConta.eu](/)
