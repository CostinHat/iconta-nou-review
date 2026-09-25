---
title: "Pot cere amânarea începerii inspecției fiscale?"
description: "Condițiile și termenul în care un contribuabil poate solicita amânarea datei de începere a unei inspecții fiscale, potrivit Codului de procedură fiscală."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Pot cere amânarea începerii inspecției fiscale?

Da, dar dreptul este limitat: legea permite o singură cerere de amânare, motivată, și doar dacă inspecția fiscală a fost anunțată în prealabil printr-un aviz de inspecție fiscală (nu și în situațiile de excepție în care avizul se comunică chiar la începerea controlului). Decizia rămâne la latitudinea conducătorului activității de inspecție fiscală.

## Temeiul legal

::: ghid-temei
„în cazul prevăzut la alin. (2), după primirea avizului de inspecție fiscală, contribuabilul/plătitorul poate solicita, o singură dată, pentru motive justificate, amânarea datei de începere a inspecției fiscale. Amânarea se aprobă sau se respinge prin decizie emisă de conducătorul activității de inspecție fiscală care se comunică contribuabilului. în cazul în care cererea de amânare a fost admisă, în decizie se menționează și data la care a fost reprogramată inspecția fiscală."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 122 alin. (5) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Cererea de amânare se poate depune **o singură dată** per acțiune de inspecție și trebuie să fie **motivată** (organul fiscal poate respinge o cerere fără justificare temeinică).
- Dreptul de a cere amânarea există doar pentru situațiile de la art. 122 alin. (2) — adică atunci când avizul de inspecție fiscală a fost comunicat înainte de începerea controlului (cu 15 zile pentru contribuabilii obișnuiți, cu 30 de zile pentru marii contribuabili).
- Avizul de inspecție fiscală trebuie, potrivit aceluiași articol, să menționeze explicit „posibilitatea de a solicita amânarea datei de începere a inspecției fiscale" — dacă acest lucru lipsește din aviz, e un indiciu de neregularitate.
- Decizia de aprobare sau respingere a amânării se comunică în scris contribuabilului, iar dacă e admisă, conține și noua dată de reprogramare.

## Ce se greșește în practică

- Se crede că amânarea se poate cere oricând în timpul inspecției — de fapt, ea privește exclusiv **data de începere**, nu suspendarea unei inspecții deja demarate.
- Se depune o a doua cerere de amânare, ignorând că legea permite o singură solicitare.
- Se confundă amânarea inspecției (art. 122) cu suspendarea inspecției fiscale (o instituție diferită, aplicabilă în alte condiții, de exemplu la controale inopinate urmate de inspecție imediată).
- Cererea se trimite fără nicio justificare sau cu motive vagi, ceea ce crește riscul de respingere.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are o funcție dedicată** pentru depunerea sau urmărirea cererilor de amânare a inspecției fiscale — acesta rămâne un demers pe care contribuabilul sau contabilul îl face direct la organul fiscal, în afara aplicației. iConta.eu are însă un modul propriu de **alerte de control fiscal** (`core/alerte_control_fiscal.py`), care rulează zilnic verificări încrucișate (TVA, D112, D390, cotă TVA) și notifică echipa contabilă atunci când apar riscuri fiscale în roșu la o firmă — dar acesta este un instrument intern al aplicației, diferit de avizul oficial de inspecție fiscală emis de ANAF, și nu automatizează procedura de amânare descrisă mai sus.

[iConta.eu](/)
