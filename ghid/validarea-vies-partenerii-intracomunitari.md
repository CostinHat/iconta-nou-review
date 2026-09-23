---
title: Validarea VIES pentru partenerii intracomunitari
description: Codul de TVA al unui partener dintr-un alt stat membru se verifică în VIES, sistemul oficial al Comisiei Europene — nu în registrul ANAF de CUI-uri — pentru că e singura sursă care confirmă dacă acel cod e valid pentru operațiuni intracomunitare.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Validarea VIES pentru partenerii intracomunitari

Un cod de TVA poate fi perfect valid pentru operațiuni interne în statul lui de origine și, în același timp, invalid pentru operațiuni intracomunitare — pentru că înregistrarea „normală” în scopuri de TVA și înregistrarea pentru VIES sunt lucruri distincte. De aceea validarea se face specific în VIES, nu prin verificarea existenței firmei.

## Temeiul legal

::: ghid-temei
„Scutire LIC cu drept de deducere — condiții: cod TVA valid al cumpărătorului comunicat furnizorului + dovada transportului în alt SM.” (CF art. 294 alin. 2 lit. a); simetric, la serviciile B2B intracomunitare, „client non-RO + cod valid VIES → neimpozabil în România, se declară D390 (S); fără cod valid → B2C, se facturează cu TVA românesc” (CF art. 278 alin. 2-3) — verificat în dosarul F050, sursă `cod_fiscal_227_2015_consolidat.txt` L18397+ și L17303+.
:::

Codul de TVA valid e, în ambele cazuri — livrare de bunuri sau prestare de servicii — o condiție de fond a tratamentului fiscal favorabil (scutire, respectiv neimpozabilitate în România). VIES e mecanismul prin care se confirmă acea validitate.

## Cum funcționează verificarea

Un cod de TVA intracomunitar e format dintr-un prefix de țară și un număr — de exemplu „DE123456789”. Prefixul trebuie să corespundă uneia dintre țările UE recunoscute pentru VIES (cele 27 state membre, plus „XI” pentru Irlanda de Nord, regim post-Brexit); Grecia e un caz special, prefixul legal e „EL”, nu „GR”, deși „GR” apare frecvent informal.

Interogarea propriu-zisă se face prin serviciul REST oficial VIES al Comisiei Europene, pe codul de țară și numărul separate de prefix, și întoarce dacă acel cod e valid, numele și adresa firmei asociate (când statul membru le publică), sau un mesaj de eroare dacă serviciul nu poate răspunde.

## Ce se greșește în practică

Verificarea „firma există, are CUI” nu e echivalentă cu verificarea VIES — o firmă poate fi complet legală și activă, dar neînregistrată pentru operațiuni intracomunitare la momentul respectiv. A doua greșeală: verificarea o singură dată, la începutul relației comerciale, fără reluare periodică — un cod valid azi poate fi anulat peste câteva luni, iar validitatea contează **la data operațiunii**, nu la data primei verificări.

## Ce face iConta.eu

La emiterea unei facturi către un client cu cod de TVA de prefix non-românesc, sistemul verifică automat starea codului direct în VIES — nu în registrul ANAF de CUI-uri — și afișează rezultatul (valid/invalid) sau avertismentul „VIES indisponibil” dacă serviciul european nu răspunde în timp util. Prefixul de țară e validat separat, cu normalizarea Grecia „GR”→„EL”, iar erorile sunt distincte pentru cod absent, prefix nevalid sau prefix fără număr asociat — deci mesajul primit indică exact ce anume nu e în regulă cu codul introdus.

[iConta.eu](/)
