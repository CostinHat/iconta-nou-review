---
title: "Cum verific perioadele de indisponibilitate publicate de ANAF?"
description: "De ce indisponibilitatea sistemelor informatice ANAF (SPV, portalul de depunere declarații) nu suspendă automat termenele fiscale, și ce trebuie să verifice contribuabilul înainte de a invoca o astfel de situație."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific perioadele de indisponibilitate publicate de ANAF?

Sistemele informatice ale ANAF (Spațiul Privat Virtual, portalul de depunere a declarațiilor) au, ocazional, perioade de mentenanță sau indisponibilitate tehnică anunțate public. Întrebarea practică e ce se întâmplă cu termenele de declarare care „pică" exact în astfel de intervale — iar răspunsul corect pornește de la felul în care Codul de procedură fiscală tratează, în general, comunicarea și depunerea actelor.

## Temeiul legal

::: ghid-temei
„(7) În cazul în care actul administrativ fiscal se comunică prin publicitate, acesta se consideră comunicat în termen de 15 zile de la data afișării anunțului."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 47 alin. (7) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Acest text nu vizează direct indisponibilitatea tehnică a SPV, ci arată principiul general al Codului de procedură fiscală: termenele legate de comunicarea actelor și, prin extensie, de îndeplinirea obligațiilor declarative sunt reglementate explicit, cu reguli proprii de calcul, indiferent de canalul folosit (publicitate, mijloace electronice etc.). De aici rezultă practic:

- Corpusul de acte normative disponibil nu conține o regulă generală care să suspende automat termenul de declarare doar pentru că portalul ANAF sau SPV au fost indisponibile o perioadă — o astfel de situație trebuie tratată ca excepție, documentată punctual (captură de ecran, mesaj oficial ANAF privind mentenanța), nu presupusă.
- Anunțurile de indisponibilitate se publică, de regulă, pe pagina oficială ANAF și pe portalul e-guvernare.ro — verificarea lor înainte de termenul-limită e singura modalitate de a documenta ulterior o eventuală imposibilitate obiectivă de depunere.
- Dacă declarația nu poate fi depusă electronic din cauza unei indisponibilități tehnice dovedite, practica ANAF admite, în anumite situații, invocarea acesteia ca motiv de întârziere justificată, dar sarcina probei rămâne la contribuabil.

## Ce se greșește în practică

- Se presupune că orice indisponibilitate a SPV, chiar de câteva ore, în afara zilei-limită de depunere, justifică automat o întârziere — fără dovada că indisponibilitatea a acoperit exact fereastra de timp în care contribuabilul ar fi depus declarația.
- Se lasă depunerea declarației chiar în ultima zi a termenului legal, expunând firma riscului ca o eventuală mentenanță neanunțată să blocheze depunerea fără nicio marjă de recuperare.
- Se invocă indisponibilitatea tehnică fără nicio dovadă documentată (captură de ecran, comunicat oficial ANAF), ceea ce face imposibilă susținerea ulterioară a motivului în fața organului fiscal.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu monitorizează și nu afișează** perioadele de indisponibilitate publicate de ANAF pentru SPV sau portalul de depunere. Aplicația urmărește termenele de declarare pe baza calendarului fiscal (`core/scadente.py`, `core/control_fiscal_api.py`), dar verificarea stării de funcționare a sistemelor ANAF în ziua depunerii rămâne responsabilitatea contabilului, direct pe canalele oficiale ANAF.

[iConta.eu](/)
