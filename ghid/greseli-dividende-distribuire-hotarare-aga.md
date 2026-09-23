---
title: "Greșeli la dividende: distribuire fără hotărâre AGA"
description: Cea mai gravă greșeală practică e distribuirea unei sume fără documentul de aprobare care s-o susțină, urmată de omiterea din D205 a dividendelor distribuite dar neplătite la 31 decembrie — o eroare confirmată direct în mecanismul de generare al declarației.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Greșeli la dividende: distribuire fără hotărâre AGA

Distribuirea dividendelor fără o hotărâre AGA (sau decizie a asociatului unic) valabilă e o problemă de drept societar, nu una fiscală — Legea societăților (Legea 31/1990) cere un astfel de document ca precondiție a oricărei distribuiri legale, deși textul exact al acestei cerințe nu face parte din corpusul verificat pentru acest ghid. Ce putem confirma cu certitudine e ce se întâmplă mai departe, în contabilitate și în declarația D205, odată ce distribuirea a fost înregistrată.

## Temeiul legal

::: ghid-temei
**Art. 97 alin. (7) din Codul fiscal**: „Veniturile sub formă de dividende [...] se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor [...]"
:::

Notă: existența unei hotărâri valide de distribuire (AGA sau decizie asociat unic) e o condiție de drept societar prevăzută de Legea 31/1990, referită generic în documentația internă a aplicației, dar textul ei exact nu a fost verificat independent pentru acest ghid — pentru detalii procedurale, consultați direct legea societăților.

## Greșelile confirmate cel mai frecvent

**1. Notă contabilă nevalidată.** D205 citește distribuirile/plățile de dividende exclusiv din notele contabile pe contul 457 aflate în status „validată" — o distribuire înregistrată dar nevalidată în contabilitate nu ajunge deloc în declarație, indiferent dacă în spatele ei există sau nu o hotărâre corectă.

**2. Dividende distribuite, dar neplătite la 31 decembrie, omise din declarație.** Aceasta e cea mai gravă și mai frecventă capcană tehnică: dacă dividendul e distribuit (creditat în 457) într-un an, dar nu e plătit până la 31 decembrie, el trebuie totuși inclus în declarația aferentă anului distribuirii — omiterea lui înseamnă pierderea obligației fiscale din evidență.

**3. Beneficiar nerezident tratat greșit.** Un beneficiar fără CNP românesc valid nu poate fi declarat pe D205 — dividendele către nerezidenți se declară pe D207, nu pe D205.

## Ce se greșește în practică

Pe lângă lipsa hotărârii AGA propriu-zise, cea mai costisitoare greșeală e presupunerea că „dacă dividendul a fost aprobat, obligația fiscală apare automat oriunde e nevoie" — fără o notă contabilă validată pe 457, nimic din acest lanț nu ajunge automat în D205.

## Ce face iConta.eu

D205 se generează automat din notele contabile validate pe contul 457 și din cotele asociaților, nu dintr-un ecran separat de introducere a dividendelor. Verificarea existenței și validității hotărârii AGA/deciziei asociatului unic rămâne complet în afara aplicației — e o condiție de drept societar, verificată înainte ca operațiunea să fie înregistrată contabil. Ce aplicația confirmă, la generare: rezidența fiecărui beneficiar (derivată din CNP), validarea checksum a CNP-urilor, și o reconciliere independentă a bazei/impozitului pe fiecare beneficiar, care blochează generarea la orice divergență.

[iConta.eu](/)
