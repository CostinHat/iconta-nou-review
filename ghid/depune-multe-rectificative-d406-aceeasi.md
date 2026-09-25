---
title: "Pot depune mai multe rectificative D406 pentru aceeași perioadă?"
description: "Legea nu limitează numărul de declarații rectificative D406 pentru o perioadă, dar impune o regulă strictă: fiecare corecție se face prin retransmiterea integrală a fișierului SAF-T, niciodată parțial."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Pot depune mai multe rectificative D406 pentru aceeași perioadă?

Da — legea nu pune o limită numărului de declarații rectificative D406 pe care le poți depune pentru aceeași perioadă de raportare. Ce contează e o regulă diferită, mai strictă decât „câte": fiecare rectificativă trebuie să conțină fișierul SAF-T **complet**, corectat integral — nu doar înregistrările sau câmpurile greșite.

## Temeiul legal

::: ghid-temei
„6. În situaţia în care contribuabilul constată anumite erori în declaraţia depusă iniţial, acesta poate depune declaraţii rectificative.
11. Pentru declaraţia informativă D406 transmisă cu erori identificate de Agenţia Naţională de Administrare Fiscală şi pentru care a fost comunicată recipisa ce le semnalează, contribuabilul retransmite integral Declaraţia informativă D406, care trebuie să cuprindă fişierul SAF-T corectat.
12. Nu este admisă transmiterea unor corecţii parţiale prin transmiterea selectivă a înregistrărilor sau câmpurilor corectate pentru Declaraţia informativă D406 anterior transmisă şi pentru care au fost primite recipise ce semnalau erori."
— OPANAF 1783/2021, Anexa 4, pct. 6, 11, 12 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

- Textul folosește pluralul „declarații rectificative" (pct. 6), fără plafon numeric — poți corecta de câte ori constați o eroare nouă, atâta timp cât fiecare corecție respectă regula de la pct. 11-12.
- Există două situații distincte care declanșează o rectificativă: (a) contribuabilul își găsește singur o eroare (pct. 6) — poate corecta din proprie inițiativă; (b) ANAF semnalează erori printr-o recipisă (pct. 11) — atunci retransmiterea integrală e obligatorie, nu opțională.
- Interdicția de la pct. 12 e explicită și fără excepție: nu se admit corecții parțiale, selective, pe înregistrări sau câmpuri — fiecare rectificativă e un fișier SAF-T întreg.

## Ce se greșește în practică

- Se încearcă retrimiterea doar a secțiunii greșite (de exemplu doar `MasterFiles` sau doar tranzacțiile dintr-o lună), crezând că ANAF „suprascrie" selectiv — practica e explicit interzisă la pct. 12.
- Se presupune că există un plafon la numărul de rectificative (ex. „doar una pe perioadă") — legea nu prevede așa ceva; ce prevede e forma corecției (integrală), nu numărul ei.
- Se ignoră distincția dintre rectificativa din proprie inițiativă (pct. 6) și cea impusă de o recipisă cu erori (pct. 11) — a doua nu e opțională, iar termenul de răspuns la recipisă contează separat de decizia de a corecta voluntar.

## Ce face iConta.eu

Codul nu tratează D406 ca pe un caz special de „rectificativă" — nu există în modulul D406 nicio noțiune dedicată de corecție sau versiune rectificativă a SAF-T-ului. O redepunere pentru aceeași perioadă parcurge exact fluxul generic al oricărei declarații: se generează din nou fișierul, intră în coada de aprobare, trece prin controlul „patru ochi" și se depune. Ce permite tehnic o a doua depunere pentru aceeași perioadă, chiar după ce prima a fost deja marcată „depusă", e regula de unicitate a cozii de aprobare, care exclude explicit starea „depusă" din verificarea de coliziune — deci un element nou poate fi adăugat în coadă pentru același tenant/tip/perioadă imediat după o depunere anterioară.

Fiecare depunere nouă e păstrată separat, cu XML-ul și rândurile ei proprii, într-un jurnal versionat care nu suprascrie depunerile anterioare — deci nu se pierde istoricul rectificativelor succesive, la nivel de bază de date. Ce nu verifică aplicația automat: dacă fișierul SAF-T retransmis respectă efectiv regula de completitudine de la pct. 11-12 (că e integral, nu parțial) rămâne responsabilitatea contabilului la generarea declarației, nu o validare dedicată în cod pentru acest caz specific.

[iConta.eu](/)
