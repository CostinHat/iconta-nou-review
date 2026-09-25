---
title: "Cum migrez datele SAF-T de la un program la altul"
description: "Ce spune legea despre continuitatea raportării SAF-T (D406) când o firmă schimbă programul de contabilitate în cursul anului, și cum se corectează eventualele erori."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum migrez datele SAF-T de la un program la altul

Legea nu reglementează tehnic „migrarea" datelor SAF-T între două programe de contabilitate — asta e o chestiune de fluxuri de lucru, nu de drept fiscal. Ce reglementează, în schimb, e obligația de continuitate a raportării D406 și mecanismul de corectare a erorilor apărute, inclusiv cele generate de o schimbare de sistem.

## Temeiul legal

::: ghid-temei
„6. În situația în care contribuabilul constată anumite erori în declarația depusă inițial, acesta poate depune declarații rectificative."
— Ordinul președintelui A.N.A.F. nr. 1.783/2021, Instrucțiuni de completare D406, pct. 6 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Nu am găsit un temei specific pentru procedura tehnică de migrare a datelor SAF-T între programe — principiul de mai sus e cel mai apropiat aplicabil, aplicat prin extensie la situația unei schimbări de software:

- Obligația de raportare D406 rămâne **neîntreruptă** indiferent de programul folosit intern — firma trebuie să continue să transmită declarația la termenele obișnuite (ultima zi a lunii următoare perioadei de raportare), chiar dacă tocmai a schimbat sistemul.
- Dacă, în urma migrării, apar erori în datele deja transmise (solduri de deschidere greșite, active duplicate, cont analitic schimbat), contribuabilul are dreptul — și practic obligația de bună-credință — să depună **declarații rectificative** pentru perioadele afectate.
- Perioada de grație pentru raportarea SAF-T (6 luni pentru prima raportare, 5 luni pentru a doua, 4 pentru a treia, 3 pentru a patra, 2 pentru a cincea, pentru cei cu obligație lunară de transmitere) există tocmai pentru a acomoda dificultăți inițiale de implementare — dar ea se aplică o singură dată, la debutul obligației firmei, nu la fiecare schimbare de furnizor de software.
- Secțiunea „Active" se depune o singură dată pe an, la termenul situațiilor financiare — schimbarea de program între două raportări anuale de acest tip nu creează, de regulă, o discontinuitate vizibilă pentru ANAF, atât timp cât soldurile de active coincid.

## Ce se greșește în practică

- Se presupune că schimbarea programului de contabilitate „resetează" obligația SAF-T sau oferă din nou perioada de grație — grația se acordă o singură dată, per contribuabil, nu per software folosit.
- Nu se verifică soldurile de deschidere din noul program față de soldurile de închidere raportate anterior în SAF-T, ceea ce poate crea discontinuități între declarațiile succesive.
- Se amână corectarea erorilor descoperite după migrare, deși legea permite explicit declarații rectificative pentru orice perioadă anterioară afectată.
- Se schimbă structura conturilor analitice fără să se păstreze o hartă de corespondență cu structura veche, complicând ulterior orice verificare încrucișată a organului fiscal pe perioade succesive.

## Ce face iConta.eu

iConta.eu are module dedicate de import al datelor unei firme la trecerea dintr-un alt sistem (`articole_import_api.py` — articole și stoc inițial, `mijloace_fixe_import_api.py` — registrul de mijloace fixe, `salariati_import_api.py` — salariați, `asociati_import_api.py`, `istoric_declaratii_import_api.py` — istoricul declarațiilor deja depuse), fiecare citind un export .xlsx/.csv din aplicația veche. Corecție necesară: numele de fișier `migrare_*.py` din cod NU sunt module de import de date ale unei firme, ci migrări de schemă (DDL) ale bazei de date proprii a aplicației, fără legătură cu trecerea de la alt program de contabilitate. Nu am găsit o funcție dedicată de export al datelor SAF-T dintr-un format specific pentru a fi „migrate" către alt program terț. Din perspectiva generării SAF-T, aplicația construiește fișierul D406 (secțiunile Active și Stocuri incluse) din datele curente ale firmei existente în iConta.eu, indiferent de programul folosit anterior — responsabilitatea reconcilierii soldurilor de deschidere cu ultima raportare din vechiul program revine contabilului, la migrarea inițială.

[iConta.eu](/)
