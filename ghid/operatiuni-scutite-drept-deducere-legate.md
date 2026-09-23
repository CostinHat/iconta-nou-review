---
title: "Operațiuni scutite cu drept de deducere legate de export"
description: Scutirea cu drept de deducere la export înseamnă taxă colectată zero, nu pierderea dreptului de a deduce TVA aferentă achizițiilor legate de operațiune.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Operațiuni scutite cu drept de deducere legate de export

Livrările de bunuri expediate în afara Uniunii Europene intră într-o categorie specifică de scutire: "scutire cu drept de deducere". Diferența față de o scutire obișnuită este esențială — firma nu colectează TVA la vânzare, dar își păstrează integral dreptul de a deduce TVA-ul aferent achizițiilor legate de acea operațiune.

## Temeiul legal

::: ghid-temei
„Sunt scutite de taxă: a) livrările de bunuri expediate sau transportate în afara Uniunii Europene de către furnizor sau de altă persoană în contul său; ... b) livrările de bunuri expediate sau transportate în afara Uniunii Europene de către cumpărătorul care nu este stabilit în România sau de altă persoană în contul său [...]"

— Codul fiscal (Legea 227/2015 consolidat), art. 294 alin. (1) lit. a)-b)
:::

Textul acoperă două scenarii de export: cel organizat de furnizorul din România, care expediază sau transportă bunul el însuși ori prin altcineva în contul său (lit. a), și cel organizat de un cumpărător care nu este stabilit în România, dar care preia bunul și îl scoate el însuși din UE (lit. b). În ambele cazuri, natura scutirii e aceeași — "cu drept de deducere" — ceea ce o deosebește fundamental de scutirile fără acest drept (aplicabile altor tipuri de operațiuni, nereglementate de art. 294): la export, deși nu se colectează TVA la vânzare, TVA-ul plătit la achizițiile legate de mărfurile exportate rămâne integral deductibil.

## Ce se greșește în practică

- Se presupune că "scutit de TVA" înseamnă automat că nici TVA-ul de pe achizițiile aferente nu mai poate fi dedus — la export, dreptul de deducere se păstrează integral, tocmai pentru că scutirea e "cu drept de deducere".
- Se aplică scutirea de export fără verificarea dovezii vamale (DVE) doar pe baza faptului că bunul e destinat unui client din afara UE — condiția legală e dovada ieșirii efective din UE, nu doar intenția sau destinația declarată.
- Se tratează la fel din punct de vedere al TVA orice ieșire de bunuri din țară, fără a distinge dacă bunul rămâne în Uniunea Europeană (livrare intracomunitară) sau iese din UE (export propriu-zis, sub art. 294).

## Ce face iConta.eu

Pentru operațiunile de export extracomunitar, aplicația validează întâi condițiile de fond ale scutirii — țara clientului (obligatorie) și existența dovezii vamale a exportului (DVE). Fără dovadă, operațiunea este respinsă cu mesajul explicit că scutirea prevăzută la art. 294 alin. (1) lit. a) nu se justifică și facturarea trebuie făcută cu TVA până la obținerea dovezii.

Odată confirmată scutirea, aplicația generează automat nota contabilă a livrării — contul de venit (implicit 707) față de contul de client (4111), doar cu valoarea operațiunii, fără nicio linie de TVA colectată. Această absență a liniei de TVA reflectă exact natura scutirii cu drept de deducere: taxa colectată e zero, dar acest lucru nu afectează în niciun fel dreptul firmei de a deduce TVA-ul aferent achizițiilor legate de operațiunea de export, drept care se gestionează separat, prin evidența generală a deducerilor firmei.

[iConta.eu](/)
