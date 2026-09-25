---
title: "Se aplică amendă dacă depun o declarație rectificativă?"
description: "Ce spune Codul de procedură fiscală despre depunerea unei declarații rectificative (formularul 710) și în ce situații se aplică efectiv o amendă contravențională."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se aplică amendă dacă depun o declarație rectificativă?

Mulți contabili amână corectarea unei declarații greșite din teama unei amenzi. Legea tratează însă declarația rectificativă ca pe un drept al contribuabilului, nu ca pe o faptă sancționabilă — amenda vizează altceva: nedepunerea sau completarea greșită a declarației inițiale, nu gestul de a o corecta.

## Temeiul legal

::: ghid-temei
„ART. 105 Corectarea declarației fiscale (1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale. [...] (3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative."
— Legea 207/2015 (Codul de procedură fiscală), art. 105 (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

::: ghid-temei
„ART. 336 Contravenții (1) Constituie contravenții următoarele fapte, dacă nu au fost săvârșite în astfel de condiții încât să fie considerate, potrivit legii, infracțiuni: [...] b) neîndeplinirea de către contribuabil/plătitor la termen a obligațiilor de declarare prevăzute de lege, a bunurilor și veniturilor impozabile sau, după caz, a impozitelor, taxelor, contribuțiilor și a altor sume, precum și orice informații în legătură cu impozitele, taxele, contribuțiile, bunurile și veniturile impozabile, dacă legea prevede declararea acestora."
— Legea 207/2015 (Codul de procedură fiscală), art. 336 alin. (1) lit. b) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă din cele două texte:

- Depunerea unei declarații rectificative e un **drept explicit al contribuabilului** (art. 105), exercitabil pe toată perioada de prescripție — gestul de a corecta, prin el însuși, nu e listat printre faptele sancționate contravențional la art. 336.
- Contravenția de la art. 336 alin. (1) lit. b) vizează **neîndeplinirea la termen a obligației de declarare** — adică o declarație inițială nedepusă, depusă greșit sau incompletă. Amenda, dacă se aplică, sancționează starea de fapt de la momentul declarației inițiale, nu decizia ulterioară de a o corecta.
- Corectarea voluntară nu elimină automat riscul unei sancțiuni pentru fapta inițială, dacă ANAF o constată separat (de exemplu, printr-un control), dar reduce practic expunerea: o eroare corectată din proprie inițiativă, înainte de un control, nu mai apare ca „declarație nedepusă/incorectă" la data verificării.
- Pe lângă o eventuală amendă, o rectificativă care majorează o obligație de plată atrage dobânzi/penalități de întârziere, calculate de la scadența inițială a creanței, nu de la data rectificativei — un cost distinct de amenda contravențională, dar la fel de real.

## Ce se greșește în practică

- Se amână depunerea unei rectificative din teama unei amenzi „pentru că am greșit declarația" — deși legea sancționează nedepunerea/eroarea nedeclarată, nu corectarea ei.
- Se confundă amenda contravențională (posibilă doar dacă ANAF constată separat fapta inițială) cu dobânzile/penalitățile de întârziere (care se datorează aproape întotdeauna când rectificativa majorează suma de plată) — sunt două sancțiuni diferite, cu mecanisme diferite.
- Se presupune că orice rectificativă atrage automat o verificare sau o sancțiune din partea ANAF, deși corectarea din proprie inițiativă e explicit prevăzută de lege ca drept al contribuabilului.

## Ce face iConta.eu

Pentru corectarea obligațiilor de impozit micro (cod 121) și impozit pe profit (cod 103) declarate prin formularul 100, iConta.eu generează declarația rectificativă **710**, din ecranul Declarații. Contabilul alege perioada, introduce codul obligației corectate, suma declarată inițial și suma corectă (plus cota de impozit, la codul 121), iar aplicația construiește XML-ul conform structurii oficiale a formularului 710 și îl validează cu validatorul oficial ANAF înainte de generare.

iConta.eu **nu calculează automat dobânzile sau penalitățile de întârziere** rezultate dintr-o rectificativă — declarația 710 doar corectează suma declarată; accesoriile, dacă se datorează, rămân de calculat separat, conform regulilor Codului de procedură fiscală. De asemenea, aplicația nu confirmă automat în SPV dacă rectificativa a înlocuit declarația inițială — acea confirmare se face de contabil, direct pe portalul ANAF.

[iConta.eu](/)
