---
title: "Ce este notificarea de conformare trimisă de ANAF?"
description: "Rolul notificării de conformare pe care ANAF o trimite contribuabililor cu risc fiscal ridicat, înainte de a-i selecta pentru inspecție fiscală."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce este notificarea de conformare trimisă de ANAF?

Notificarea de conformare este un instrument prin care organul de inspecție fiscală îi dă contribuabilului o ultimă șansă de a-și corecta situația fiscală înainte de a fi selectat efectiv pentru o inspecție fiscală. Practic, ANAF semnalează riscurile identificate și acordă un termen pentru remediere, evitând astfel — dacă acesta este folosit corect — declanșarea unui control.

## Temeiul legal

::: ghid-temei
„(1) Pentru contribuabilii/plătitorii prezumtivi a fi selectați pentru efectuarea inspecției fiscale, organul de inspecție fiscală transmite acestora, în scris, o notificare de conformare cu privire la riscurile fiscale identificate în scopul reanalizării de către aceștia a situației fiscale și, după caz, de a depune sau de a corecta declarațiile fiscale. (2) Prin notificare se comunică contribuabilului/plătitorului că în termen de 30 de zile de la data comunicării notificării are posibilitatea să depună sau să corecteze declarațiile fiscale. Până la expirarea acestui termen, organul de inspecție fiscală nu întreprinde nicio acțiune în vederea selectării pentru efectuarea inspecției fiscale."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 121^1 alin. (1)-(2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Notificarea vizează contribuabilii **prezumtivi a fi selectați** pentru inspecție fiscală — deci nu înseamnă că inspecția e deja decisă, ci că profilul de risc al firmei a atras atenția organului fiscal.
- Termenul de reacție este de **30 de zile** de la comunicare, timp în care contribuabilul poate depune sau corecta declarațiile fiscale, iar ANAF nu întreprinde acțiuni de selectare pentru inspecție.
- Depunerea sau corectarea declarațiilor **nu blochează definitiv** selectarea pentru inspecție — potrivit alin. (3), aceasta rămâne posibilă, dar numai după împlinirea termenului de 30 de zile.
- Contribuabilii cu risc fiscal ridicat care **nu remediază** riscurile semnalate în termen sunt supuși, potrivit alin. (4), în mod obligatoriu unei inspecții fiscale sau unei verificări documentare.

## Ce se greșește în practică

- Se ignoră notificarea, considerând-o o simplă informare fără consecințe — de fapt, netratarea ei duce direct la inspecție fiscală obligatorie.
- Se așteaptă până aproape de expirarea celor 30 de zile pentru a analiza riscurile semnalate, deși pregătirea corecțiilor (mai ales dacă implică declarații rectificative complexe) necesită timp.
- Se presupune că depunerea unei declarații rectificative în acest interval garantează evitarea inspecției — legea spune explicit că doar amână, nu elimină, posibilitatea selectării.
- Se confundă notificarea de conformare cu avizul de inspecție fiscală — sunt etape distincte: prima e un semnal preventiv, al doilea anunță formal declanșarea controlului.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu primește și nu procesează automat** notificările de conformare emise de ANAF — acestea ajung la contribuabil prin Spațiul Privat Virtual sau prin poștă, în afara aplicației. iConta.eu are însă un modul propriu de **alerte de control fiscal** (`core/alerte_control_fiscal.py`), care rulează zilnic verificări încrucișate interne (TVA, D112, D390, cotă TVA) și trimite o notificare în clopotelul aplicației atunci când o firmă are riscuri fiscale în roșu — un mecanism preventiv asemănător ca scop, dar complet distinct de notificarea oficială de conformare descrisă mai sus, care rămâne exclusiv un instrument al ANAF.

[iConta.eu](/)
