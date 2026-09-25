---
title: "Cum evit poprirea dacă firma nu poate plăti toate taxele la termen?"
description: "Eșalonarea la plată suspendă executarea silită (inclusiv poprirea), potrivit Codului de procedură fiscală, dacă decizia de eșalonare este comunicată înainte de continuarea executării."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum evit poprirea dacă firma nu poate plăti toate taxele la termen?

Când firma nu poate achita integral obligațiile fiscale la termen, legea oferă o cale explicită de evitare a popririi: eșalonarea la plată, care suspendă executarea silită de la data comunicării deciziei — nu doar o promisiune administrativă, ci un efect juridic direct.

## Temeiul legal

::: ghid-temei
„(1) Pentru sumele care fac obiectul eșalonării la plată a obligațiilor fiscale, precum și pentru obligațiile prevăzute la art. 194 alin. (1) lit. a) - c), e) - j) și n) nu începe sau se suspendă, după caz, procedura de executare silită, de la data comunicării deciziei de eșalonare la plată. În cazul obligațiilor prevăzute la art. 194 alin. (1) lit. f), executarea silită se suspendă după comunicarea somației."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 203 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă din text pentru o firmă aflată în dificultate de plată:

- Depunerea la timp a unei **cereri de eșalonare la plată**, urmată de o decizie favorabilă comunicată de organul fiscal, **oprește sau suspendă** procedura de executare silită — deci și poprirea conturilor bancare.
- Dacă somația a fost deja comunicată pentru o obligație aflată sub incidența eșalonării, executarea silită se suspendă **după** comunicarea somației, nu se anulează retroactiv — momentul cererii contează.
- Respectarea ulterioară a graficului de eșalonare este condiția pentru menținerea suspendării — nerespectarea lui reactivează procedura de executare silită.

## Ce se greșește în practică

- Se așteaptă până după primirea somației de executare silită pentru a solicita eșalonarea, deși cererea depusă din timp reduce riscul ca poprirea să fie deja declanșată.
- Se presupune că simpla depunere a cererii de eșalonare suspendă automat executarea — suspendarea produce efecte de la **comunicarea deciziei** de eșalonare, nu de la depunerea cererii.
- Se ignoră graficul de eșalonare aprobat, considerând că odată obținută eșalonarea „problema e rezolvată" — nerespectarea ratelor readuce firma sub executare silită.

## Ce face iConta.eu

Verificat în cod: `core/control_fiscal_api.py` și `core/alerte_control_fiscal.py` semnalează, pentru fiecare firmă, verificatorii aflați în „roșu" (de exemplu TVA sau D112 neconcordante cu evidența contabilă) și trimit notificări agregate contabililor cabinetului atunci când apare un risc nou; aplicația nu are, la acest moment, un flux de generare sau depunere a cererii de eșalonare la plată — inițierea și urmărirea eșalonării rămân, deocamdată, în sarcina contabilului/angajatorului, în afara aplicației.

[iConta.eu](/)
