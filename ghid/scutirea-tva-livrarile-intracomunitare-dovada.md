---
title: "Scutirea de TVA pentru livrările intracomunitare: dovada transportului"
description: "Condițiile legale ale scutirii de TVA la livrarea intracomunitară — codul valabil de TVA al cumpărătorului și declarația recapitulativă corect depusă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Scutirea de TVA pentru livrările intracomunitare: dovada transportului

Scutirea de TVA la o livrare intracomunitară de bunuri nu e automată — legea leagă expres această scutire de două condiții cumulative ale furnizorului: codul valabil de TVA al cumpărătorului și corectitudinea declarației recapitulative (D390). Fără ele, scutirea poate fi refuzată chiar dacă transportul bunurilor în alt stat membru a avut loc efectiv.

## Temeiul legal

::: ghid-temei
„Sunt, de asemenea, scutite de taxă următoarele: a) livrările intracomunitare de bunuri către o persoană impozabilă [...] care acționează ca atare în alt stat membru [...], care îi comunică furnizorului un cod valabil de înregistrare în scopuri de TVA, atribuit de autoritățile fiscale din alt stat membru [...] Scutirea prevăzută la alin. (2) lit. a) nu se aplică în cazul în care furnizorul nu a respectat obligația [...] de a depune o declarație recapitulativă sau declarația recapitulativă depusă de acesta nu conține informațiile corecte referitoare la această livrare [...], cu excepția cazului în care furnizorul poate justifica în mod corespunzător deficiența într-un mod considerat satisfăcător de autoritățile fiscale competente."
— Legea 227/2015 (Codul fiscal), art. 294 alin. (2) lit. a) și alin. (2^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.html)
:::

Structura scutirii, așa cum rezultă din text:

- **Condiția 1 — codul valabil de TVA al cumpărătorului**, comunicat furnizorului și atribuit de statul membru de destinație (art. 294 alin. 2 lit. a).
- **Condiția 2 — declarația recapitulativă (D390) corectă și depusă**, cu informațiile exacte despre livrare; nedepunerea sau completarea greșită anulează scutirea, cu excepția unei justificări satisfăcătoare pentru autoritatea fiscală (art. 294 alin. 2^1).
- **Documentele care justifică efectiv transportul** (dovada fizică a expedierii bunurilor) rămân stabilite prin ordin al ministrului finanțelor publice, potrivit delegării din art. 294 alin. (3) — actul de aplicare care fixează exact ce documente se acceptă nu se află printre sursele consultate pentru acest ghid, deci nu poate fi citat aici.

## Ce se greșește în practică

- Se tratează dovada transportului ca fiind suficientă de una singură, ignorând faptul că legea leagă scutirea explicit de codul de TVA valabil al cumpărătorului și de corectitudinea D390 (art. 294 alin. 2 lit. a și alin. 2^1).
- Se emite factura scutită fără să se verifice în prealabil, prin VIES, dacă respectivul cod de TVA e încă valabil la data livrării.
- Se depune D390 cu întârziere sau cu date incomplete și apoi se presupune că scutirea de TVA rămâne automat valabilă — art. 294 alin. (2^1) o condiționează explicit de corectitudinea acelei declarații.

## Ce face iConta.eu

Nu am identificat în codul iConta.eu o funcție care să verifice automat, la emiterea facturii, validitatea codului de TVA al cumpărătorului în VIES sau care să blocheze scutirea de TVA în lipsa acestei verificări. Ce am confirmat este generarea declarației D390 (`core/d390.py`), cu clasificare și reconciliere proprii — dar corelarea explicită a scutirii de TVA a fiecărei facturi cu depunerea corectă a D390, conform art. 294 alin. (2^1), rămâne o verificare pe care contabilul o face manual, nu una automatizată în aplicație.

[iConta.eu](/)
