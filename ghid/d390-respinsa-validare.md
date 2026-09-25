---
title: "Ce fac dacă D390 este respinsă la validare?"
description: "Ce verifică ANAF după depunerea D390, cum funcționează validarea locală înainte de trimitere în iConta.eu și ce înseamnă o notificare de corecție."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă D390 este respinsă la validare?

O declarație D390 poate fi „respinsă" în două momente diferite: la validarea structurală, înainte de a fi trimisă (fișierul XML nu respectă schema oficială), sau după depunere, când ANAF face propria verificare formală a conținutului și poate cere corectarea declarației.

## Temeiul legal

::: ghid-temei
„2. Verificarea formală a declaraţiilor recapitulative. Pentru fiecare declaraţie recapitulativă organul fiscal competent verifică: a) corectitudinea codului de înregistrare în scopuri de TVA al persoanei impozabile care realizează operaţiuni intracomunitare, prin verificarea datelor de identificare din declaraţie cu cele existente în Registrul contribuabililor; b) integralitatea codurilor de înregistrare în scopuri de TVA ale operatorilor străini înscrişi în declaraţia recapitulativă: înscrierea corectă a codului de ţară, precum şi a numărului de caractere ale codului. [...] 3.1. După prelucrarea declaraţiilor recapitulative vor fi identificate persoanele impozabile care au depus declaraţii recapitulative ce prezintă erori, potrivit pct. 2, iar pentru aceste persoane se emit notificări pentru corectarea declaraţiei."
— OPANAF 705/2020, Anexa 2, Instrucțiuni pct. 2-3.1 (sursă: anaf_surse/opanaf_705_2020_d390.txt)
:::

Din text rezultă că respingerea „la validare", în sensul unei verificări oficiale a conținutului, se întâmplă **după** depunere, nu în timp real la încărcare:

- ANAF verifică, printre altele, corectitudinea codului de TVA propriu (comparat cu Registrul contribuabililor) și dacă toate codurile partenerilor străini sunt complete;
- dacă găsește erori, organul fiscal emite o **notificare de corectare a declarației**, nu o respinge automat fără explicație;
- contribuabilul are obligația să redepună o declarație corectată, ca răspuns la notificare.

## Ce se greșește în practică

- Se presupune că, odată trimisă declarația, nu mai există nicio cale de corecție — de fapt, procedura oficială presupune tocmai o etapă de notificare și corectare.
- Se ignoră notificarea de corecție a ANAF sau se răspunde cu întârziere, fără să se verifice exact ce cod de TVA sau ce câmp a fost semnalat ca eronat.
- Se confundă o eroare de validare structurală (XML invalid, câmp obligatoriu lipsă) cu o eroare de conținut constatată ulterior de ANAF (cod de partener incorect) — cele două au cauze și momente diferite.

## Ce face iConta.eu

Înainte ca fișierul D390 să fie considerat gata de depus, aplicația rulează **local** validatorul oficial ANAF instalat (DUK), la fel ca pentru celelalte declarații fiscale generate — acest pas prinde erorile structurale (cod obligatoriu lipsă pentru operațiunile L/T/P/R, țară invalidă, format greșit) înainte ca fișierul să ajungă la ANAF, nu după.

Ce nu face aplicația: nu depune automat declarația în SPV (depunerea rămâne manuală, cu fișierul deja validat local) și nu generează automat o declarație rectificativă marcată ca atare dacă ANAF semnalează o eroare de conținut după depunere — motorul D390 nu are, la data acestui ghid, un parametru care să bifeze automat căsuța de „rectificativă" pe formular. Dacă primiți o notificare de corecție de la ANAF, corectarea propriu-zisă a datelor (cod de partener, reclasificare) se face în aplicație, dar bifarea și depunerea declarației rectificative rămân un pas manual, prin SPV.

[iConta.eu](/)
