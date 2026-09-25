---
title: "Cum verific D406 cu balanța contabilă?"
description: "De ce trebuie ca fișierul SAF-T (D406) să se lege de balanța de verificare lunară și ce pași concreți sunt de urmat pentru reconciliere."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific D406 cu balanța contabilă?

D406 (SAF-T) nu e o declarație inventată separat de contabilitate — secțiunea ei centrală, `GeneralLedgerEntries`, este chiar Registrul-jurnal, iar Registrul-jurnal trebuie să corespundă balanței de verificare lunare. Dacă fișierul depus la ANAF nu se leagă de balanța cu care contabilul lucrează, înseamnă că undeva un cont, o notă sau o linie s-a pierdut sau s-a dublat între contabilitate și declarație.

## Temeiul legal

::: ghid-temei
„Pentru verificarea înregistrării corecte în contabilitate a operațiunilor efectuate, lunar se întocmește balanța de verificare."
— Legea nr. 82/1991 a contabilității, art. 22 (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Iar structura oficială a fișierului SAF-T confirmă legătura directă: secțiunea obligatorie „Înregistrări Contabile - Registrul Jurnal" (`GeneralLedgerEntries`) corespunde exact Registrului-jurnal cerut de art. 20 din aceeași lege, iar art. 21 cere ca registrele contabile să fie „complet astfel completate încât să permită, în orice moment, identificarea și controlul operațiunilor contabile efectuate".

Practic, verificarea D406 vs. balanță înseamnă:

- **Rulaj per cont**: suma debitelor și creditelor din secțiunea `GeneralLedgerEntries` a fișierului SAF-T trebuie să corespundă rulajelor din balanța de verificare a lunii/trimestrului raportat.
- **Dubla partidă**: pentru fiecare notă din SAF-T, suma debitelor trebuie să fie egală cu suma creditelor (Σdebit = Σcredit) — un dezechilibru semnalează o notă incompletă la emisie.
- **Completitudine**: nicio notă validată în perioada raportată nu trebuie să lipsească din fișier și nicio notă din afara perioadei nu trebuie inclusă din greșeală.

## Ce se greșește în practică

- Se compară D406 doar vizual, „la ochi", fără o balanță de rulaje independentă recalculată separat de generator — orice eroare de mapare (cont greșit, notă pierdută) trece neobservată.
- Se presupune că, dacă declarația a fost validată de ANAF (schema XSD e corectă), conținutul e automat corect — validarea de schemă nu verifică dacă sumele coincid cu balanța reală.
- Se ignoră diferențele mici „nesemnificative" — o diferență de câțiva lei între SAF-T și balanță e adesea semnul unei note care s-a dus pe un cont greșit, nu o eroare de rotunjire.

## Ce face iConta.eu

iConta.eu generează D406 din `core/d406.py`, dar verificarea nu se oprește la emisie: aplicația construiește o **a doua cale de calcul, independentă**, în `core/d406_reconciliere.py`. Aceasta reface balanța de rulaje per cont direct din `inregistrari_linii` (notele contabile validate din perioada de raportare), fără să reutilizeze codul generatorului D406, și o compară cu rulajele extrase din fișierul SAF-T efectiv emis. Dacă cele două nu coincid pe un cont, sau dacă suma debitelor și creditelor unei note nu e egală, aplicația oprește depunerea și arată exact contul și valorile divergente — nu corectează tacit.

Limita declarată în cod: reconcilierea acoperă secțiunea `GeneralLedgerEntries` (dubla partidă a notelor contabile); nu acoperă încă, în aceeași verificare automată, sub-secțiunile de facturi de vânzare/achiziție, plăți sau mișcări de active din D406 — acestea au verificări separate, parțiale, de reconciliere linii-antet.

[iConta.eu](/)
