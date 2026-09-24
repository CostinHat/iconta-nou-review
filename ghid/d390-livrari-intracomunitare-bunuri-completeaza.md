---
title: D390 pentru livrări intracomunitare de bunuri: cum se completează
description: Ce intră pe codul L de livrări intracomunitare scutite, de unde se ia baza și ce verifică ulterior aplicația față de decont și evidență.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# D390 pentru livrări intracomunitare de bunuri: cum se completează

Declarația recapitulativă (D390) nu se completează liber — se construiește din facturile emise către parteneri din alte state membre, grupate pe cod de operațiune. Pentru livrările de bunuri, codul relevant este **L**, iar condiția scutirii ține de un singur lucru verificabil: codul de TVA valid al cumpărătorului, la data operațiunii.

## Temeiul legal

::: ghid-temei
**Art. 325 din Codul fiscal (Legea 227/2015) — Declarația recapitulativă.** Orice persoană impozabilă înregistrată în scopuri de TVA, conform art. 316 sau art. 317, întocmește și depune o declarație recapitulativă care menționează, între altele, livrările intracomunitare de bunuri scutite de taxă (lit. a) și achizițiile intracomunitare taxabile (lit. d). Declarația se depune **lunar**, pentru fiecare lună calendaristică în care ia naștere exigibilitatea taxei.

**Condiția de scutire — art. 294 alin. (2) lit. a).** Livrarea intracomunitară e scutită cu drept de deducere numai dacă sunt îndeplinite condițiile din text, între care codul valid de TVA al cumpărătorului în alt stat membru, valabil la data operațiunii.

**Formularul (390 VIES)** — modelul și conținutul sunt aprobate prin **OPANAF 705/2020**.

**Termenul** e stabilit prin **OPANAF 6073/2024** (Monitorul Oficial nr. 771 din 7 august 2024): până la data de 25 inclusiv a lunii următoare celei în care ia naștere exigibilitatea taxei. Termenul nu mai e fixat direct în art. 325, ci prin ordin, după modificarea adusă de OUG 70/2024.
:::

Pe scurt, ce trece pe codul **L**: livrările de bunuri către un cumpărător înregistrat în scopuri de TVA în alt stat membru, cu codul valid la data livrării, scutite cu drept de deducere conform art. 294 alin. (2) lit. a). Baza declarată este valoarea facturii, pe partenerul respectiv, agregată pe perioada în care ia naștere exigibilitatea (nu neapărat luna emiterii facturii, dacă exigibilitatea cade în altă lună).

Perechea de pe partea de achiziții — codul **A** — funcționează simetric, dar pentru achizițiile intracomunitare taxabile (locul operațiunii și taxarea inversă fiind reglementate la art. 278).

## Ce se greșește în practică

- Codul de TVA al partenerului se verifică la data completării declarației, nu la data operațiunii. Un partener își poate pierde valabilitatea codului între timp — scutirea se raportează la momentul livrării, nu la momentul depunerii.
- Se confundă codul L (livrări) cu A (achiziții) pe operațiuni introduse manual, mai ales când facturarea se face din alt sistem și datele ajung agregate, fără distincția clară de direcție.
- Se ignoră exigibilitatea: o factură emisă la finalul unei luni, dar cu exigibilitate în luna următoare, trebuie să intre în recapitulativa lunii următoare, nu în cea a emiterii.

## Ce face iConta.eu

Baza pentru codurile L și A se calculează automat din facturile intracomunitare ale perioadei, pe baza clasificării partenerului (cod de TVA UE valid, CUI din altă țară membră) — nu se introduce manual, cu excepția operațiunilor care nu au corespondent de factură în sistem.

După completare și depunere, aplicația nu se oprește la generarea fișierului: rulează un control încrucișat care confruntă D390 cu evidența contabilă validată (facturile cu notă contabilă validată legată de ele) și, separat, cu rândurile de operațiuni intracomunitare din decontul de TVA (D300) efectiv depus. Acesta e însă un pas ulterior de **verificare**, nu de completare — dacă apar diferențe, primești un semnal (verde/gri/roșu), nu o corecție automată a declarației deja generate.

[iConta.eu](/)
