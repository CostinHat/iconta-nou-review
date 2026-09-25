---
title: "Cum declar un avans în D300?"
description: "Ce se întâmplă cu TVA la un avans încasat sau plătit și cum ajunge exigibilitatea lui în decontul de TVA."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum declar un avans în D300?

Un avans încasat sau plătit înainte de livrarea bunului sau prestarea serviciului naște exigibilitatea TVA la data încasării/plății lui, nu la data documentului final. Vestea bună e că, pentru un avans facturat corect, decontul de TVA nu are nevoie de o „declarare" separată — factura de avans intră în decont exact ca orice altă factură a perioadei.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile alin. (1), exigibilitatea taxei intervine: [...] b) la data la care se încasează avansul, pentru plățile în avans efectuate înainte de data la care intervine faptul generator. Avansurile reprezintă plata parțială sau integrală a contravalorii bunurilor și serviciilor, efectuată înainte de data livrării ori prestării acestora;"
— Codul fiscal (Legea 227/2015), art. 282 alin. (2) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Regula generală (art. 282 alin. (1) CF) e că TVA devine exigibilă la faptul generator (livrare/prestare). **Excepția avansului** mută exigibilitatea la data încasării.
- Consecința practică: factura de avans emisă intră, ca orice altă factură, în decontul lunii/trimestrului în care a fost emisă — nu se așteaptă factura finală pentru a „declara" TVA.
- La factura finală, valoarea deja facturată ca avans se scade din baza rămasă de facturat, iar diferența (dacă există, de exemplu la schimbare de cotă) se regularizează.

## Ce se greșește în practică

- Se amână declararea TVA a avansului până la emiterea facturii finale, deși legea cere exigibilitatea la data încasării avansului — greșeala produce o TVA colectată/dedusă înregistrată în luna greșită.
- Se tratează regularizarea de la factura finală ca pe o operațiune complet nouă, fără să se scadă corect suma deja facturată ca avans, riscând dubla declarare a aceleiași baze.
- Se caută în panoul de rânduri manuale al D300 o funcție specială „avans" — nu există un rând dedicat avansurilor în structura oficială a decontului; avansul e doar o factură ca oricare alta, cu data emiterii ca reper de exigibilitate.

## Ce face iConta.eu

Motorul D300 al iConta.eu tratează automat exigibilitatea avansului: o factură de avans emisă intră în decontul lunii de emitere, exact ca orice altă factură a perioadei, fără intervenție manuală din partea contabilului. Modulul de avansuri al aplicației generează notele contabile aferente (înregistrarea avansului și regularizarea lui la factura finală), dar aceste note contabile **nu produc rânduri separate în D300** — baza și TVA din factura de avans intră în decont prin mecanismul obișnuit de extragere a facturilor perioadei.

Dincolo de acest mecanism automat, aplicația **nu are un rând sau un flux dedicat, separat, pentru „regularizarea unui avans"** în panoul de rânduri manuale al D300 (F251) — dacă un avans nu e capturat corect (de exemplu, a fost omis din evidență sau are o eroare de cotă descoperită ulterior), corecția intră sub regula generală de regularizare a decontului (rândul de regularizări, dacă operațiunea nu are deja o factură corectă în perioada curentă), nu sub o funcție specifică de „avans" — aceasta nu există separat în aplicație.

[iConta.eu](/)
