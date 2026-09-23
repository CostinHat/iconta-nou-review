---
title: "Cum tratez fiscal creanțele prescrise?"
description: "Scoaterea din evidență a unei creanțe prescrise e, în primul rând, o obligație contabilă — dar pierderea rămasă neacoperită de provizion e deductibilă doar dacă situația se încadrează în una din cele șase excepții din Codul fiscal, iar prescripția în sine nu e una dintre ele."
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum tratez fiscal creanțele prescrise?

O creanță prescrisă (pentru care dreptul de a cere executarea silită s-a stins) trebuie scoasă din evidența contabilă — ea nu mai reprezintă un activ recuperabil pe cale legală. Problema fiscală apare la partea rămasă neacoperită de o ajustare deja constituită: deductibilitatea acestei pierderi nu decurge automat din prescripție, ci din încadrarea în una din situațiile enumerate expres de lege.

## Temeiul legal

::: ghid-temei
„Următoarele cheltuieli nu sunt deductibile: [...] h) pierderile înregistrate la scoaterea din evidență a creanțelor, pentru partea neacoperită de provizion, potrivit art. 26, precum și cele înregistrate în alte cazuri decât următoarele: 1. punerea în aplicare a unui plan de reorganizare confirmat printr-o sentință judecătorească [...]; 2. procedura de faliment a debitorilor a fost închisă pe baza hotărârii judecătorești; 3. debitorul a decedat și creanța nu poate fi recuperată de la moștenitori; 4. debitorul este dizolvat, în cazul societății cu răspundere limitată cu asociat unic, sau lichidat, fără succesor; 5. debitorul înregistrează dificultăți financiare majore care îi afectează întreg patrimoniul; 6. au fost încheiate contracte de asigurare."

*(Codul fiscal — Legea nr. 227/2015, art. 25 alin. (4) lit. h))*
:::

## Ce se deduce și ce nu

- **Dacă a fost constituită anterior o ajustare** (491), dedusă fiscal conform art. 26 (30% peste 270 de zile sau 100% la faliment/insolvență), partea deja dedusă nu se recalculează la scoaterea din evidență.
- **Partea rămasă neacoperită de ajustare** e deductibilă doar dacă situația concretă se încadrează în una din cele șase excepții de mai sus. Prescripția extinctivă, luată izolat, **nu figurează** printre ele — dacă motivul scoaterii din evidență e strict trecerea termenului de prescripție, fără să existe și o altă condiție din listă (de exemplu debitorul dizolvat fără succesor sau în dificultăți financiare majore), pierderea rămâne nedeductibilă.

## Ce se greșește în practică

- Se deduce automat toată pierderea rămasă doar pentru că dreptul de a cere executarea silită s-a prescris, fără verificarea celor șase condiții din art. 25 alin. (4) lit. h).
- Se lasă creanța prescrisă în evidență la nesfârșit, evitând scoaterea ei din bilanț, ceea ce nu e o soluție — obligația contabilă de a reflecta realitatea rămâne, indiferent de tratamentul fiscal al pierderii.
- Se confundă partea deja acoperită de o ajustare dedusă anterior cu partea rămasă, dublând sau anulând greșit deducerea.

## Ce face iConta.eu

`core/provizioane.py` calculează și contabilizează exclusiv ajustarea pentru deprecierea creanței (`deductibilitate_creanta`, art. 26) — aplicația nu modelează scoaterea propriu-zisă din evidență a unei creanțe prescrise și nu verifică dacă situația concretă a debitorului se încadrează în una din cele șase excepții de la art. 25 alin. (4) lit. h). Evaluarea și nota contabilă corespunzătoare rămân manuale, pe baza documentelor disponibile despre debitor.

[iConta.eu](/)
