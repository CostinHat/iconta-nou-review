---
title: "Cum corectez D101 după modificarea amortizării fiscale?"
description: "Condițiile în care D101 poate fi corectată prin declarație rectificativă, inclusiv după anularea rezervei verificării ulterioare, potrivit Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum corectez D101 după modificarea amortizării fiscale?

O modificare a bazei de amortizare fiscală (de exemplu, o durată normală de utilizare recalculată sau o eroare de încadrare a unui mijloc fix) schimbă rezultatul fiscal — iar D101 se corectează prin declarație rectificativă, cu reguli diferite după cum rezerva verificării ulterioare a fost sau nu anulată.

## Temeiul legal

::: ghid-temei
„(1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale. [...] (3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative. [...] (5) Declarația de impunere nu poate fi depusă și nu poate fi corectată după anularea rezervei verificării ulterioare. (6) Prin excepție de la prevederile alin. (5), declarația de impunere poate fi depusă sau corectată după anularea rezervei verificării ulterioare în următoarele situații: a) în situația în care corecția se datorează îndeplinirii sau neîndeplinirii unei condiții prevăzute de lege care impune corectarea bazei de impozitare și/sau a creanței fiscale aferente."
— Legea nr. 207/2015, art. 105 alin. (1), (3), (5), (6) lit. a) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă pentru situația concretă a amortizării modificate:

- **Regula de bază**: D101, ca declarație de impunere, poate fi corectată printr-o rectificativă oricând în interiorul termenului de prescripție a dreptului ANAF de a stabili creanțe fiscale (art. 105 alin. (1)).
- **Blocajul**: dacă rezerva verificării ulterioare a fost deja anulată pentru perioada respectivă (de exemplu în urma unei inspecții fiscale finalizate), regula generală interzice corectarea (alin. (5)).
- **Excepția care contează aici**: dacă modificarea vine din „îndeplinirea sau neîndeplinirea unei condiții prevăzute de lege care impune corectarea bazei de impozitare" — cum ar fi o recalculare a duratei normale de utilizare sau o schimbare de metodă de amortizare permisă de Codul fiscal — corecția rămâne posibilă chiar și după anularea rezervei (alin. (6) lit. a)).
- Contribuabilul trebuie să **menționeze explicit temeiul legal** al corecției în declarația rectificativă (art. 105 alin. (7)) — nu e suficient să depună o rectificativă „tăcută", fără explicația modificării.

## Ce se greșește în practică

- Se depune rectificativa fără verificarea prealabilă dacă rezerva verificării ulterioare a fost anulată pentru perioada respectivă — după anulare, o rectificativă „obișnuită" e respinsă, dacă nu se încadrează în excepțiile art. 105 alin. (6).
- Se omite menționarea temeiului legal al corecției în declarația rectificativă, deși legea o cere expres la alin. (7).
- Se corectează retroactiv amortizarea fără să se distingă dacă modificarea provine dintr-o eroare de calcul (corectabilă oricând, în termenul de prescripție) sau dintr-o schimbare de opțiune fiscală ulterioară (care poate avea reguli proprii de aplicare în timp, în Codul fiscal).

## Ce face iConta.eu

Generatorul de D101 din iConta.eu (`core/d101.py`) recalculează declarația pe baza datelor curente din aplicație de fiecare dată când e rulat (`genereaza`), inclusiv pe baza modulului de amortizare a mijloacelor fixe (`core/d406_active.py`, folosit și pentru SAF-T). Aplicația nu marchează însă automat, la data acestui ghid, o declarație regenerată drept „rectificativă" cu temeiul legal aferent din art. 105 — încadrarea corecției (rectificativă obișnuită sau excepție de la art. 105 alin. (6)) rămâne o verificare a contabilului, înainte de retransmiterea declarației.

[iConta.eu](/)
