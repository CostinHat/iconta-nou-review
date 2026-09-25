---
title: "Numerar la service auto 2026: evidență"
description: "Obligațiile legale de evidențiere a numerarului pentru un service auto care încasează de la populație: casa de marcat, bonul fiscal și plafonul de numerar."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Numerar la service auto 2026: evidență

Un service auto nu are un regim legal distinct de evidențiere a numerarului — i se aplică regulile generale valabile oricărui prestator de servicii către populație: obligația de a utiliza aparat de marcat electronic fiscal la orice încasare (integrală sau parțială, cu numerar sau card), plus plafoanele generale de numerar din Legea 70/2015 pentru operațiunile cu alte firme sau PFA (piese, subcontractare).

## Temeiul legal

::: ghid-temei
„(1) Operatorii economici care încasează, integral sau parțial, cu numerar sau prin utilizarea cardurilor de credit/debit sau a substitutelor de numerar contravaloarea bunurilor livrate cu amănuntul, precum și a prestărilor de servicii efectuate direct către populație sunt obligați să utilizeze aparate de marcat electronice fiscale."
— OUG nr. 28/1999 (republicată), art. 1 alin. (1) (sursă: anaf_surse/oug_28_1999.html)
:::

Ce înseamnă concret pentru un service auto:

- Orice reparație/intervenție facturată către o persoană fizică (client direct, proprietarul autovehiculului) și încasată integral sau parțial cu numerar sau card trebuie însoțită de bon fiscal emis cu AMEF (art. 1 alin. (1)-(2) din OUG 28/1999) — indiferent de valoarea reparației.
- Documentul de bază pentru evidența operativă a numerarului este **Registrul de casă**, prevăzut de OMFP 2634/2015: „document de înregistrare operativă a încasărilor și plăților în numerar [...]; document de stabilire, la sfârșitul fiecărei zile, a soldului de casă [...]. Registrul de casă se întocmește zilnic, pe baza documentelor justificative de încasări și plăți."
- Pentru achizițiile de piese sau subcontractarea unor lucrări către alte firme/PFA, se aplică plafonul general al Legii 70/2015: 5.000 lei/zi/persoană pentru încasări/plăți în numerar între persoane juridice/PFA (art. 3), cu interdicția de fragmentare pentru facturi mai mari.
- Dacă service-ul are plăți din avansuri spre decontare (către mecanici sau alți angajați, pentru piese cumpărate cash), se aplică plafonul separat de 5.000 lei/zi/persoană care a primit avansul (art. 3 alin. (1) lit. e)).

## Ce se greșește în practică

- Se emite factură fără bon fiscal pentru clienți persoane fizice care plătesc cu numerar sau card, considerând factura suficientă — bonul fiscal rămâne documentul obligatoriu la fiecare încasare, factura fiind eliberată suplimentar, doar la cerere.
- Se ține Registrul de casă neactualizat zilnic, deși legea impune întocmirea lui zilnică, pe baza documentelor justificative, nu retroactiv la sfârșit de lună.
- Se depășește plafonul de 5.000 lei/zi la plata furnizorilor de piese în numerar, fără verificarea cumulului zilnic pe același furnizor.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are un modul de casierie (`core/casa.py`) care ține un registru de casă cu sold rulant (`registru_casa`) și verifică automat, pe baza operațiunilor introduse, respectarea plafoanelor legale de numerar din Legea 70/2015 (`verifica_plafon`) — inclusiv pentru avansurile spre decontare. Aplicația poate importa, separat, Raportul Z generat de aparatul de marcat electronic fiscal al service-ului (`core/amef_import.py`), cu totalurile de încasări pe modalitate de plată. Aplicația nu are însă o funcționalitate specifică sectorului auto (de exemplu, legarea încasărilor de comenzi de reparație individuale) — evidența numerarului se face la nivelul general al oricărei firme cu casierie.

[iConta.eu](/)
