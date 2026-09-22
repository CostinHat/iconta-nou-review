---
title: Cum transmit o factură de corecție în RO e-Factura?
description: O factură de corecție se transmite la SPV ca orice altă factură emisă, prin fluxul obișnuit — iConta.eu nu populează câmpul de referință structurată (BillingReference/BT-25) către factura inițială în XML.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum transmit o factură de corecție în RO e-Factura?

Din punct de vedere tehnic, o factură de corecție nu are un canal separat de transmitere la SPV. Ea intră în coada obișnuită de facturi emise, cu propriul număr, exact ca orice altă factură. Ce merită înțeles înainte de a o trimite e ce anume conține — și, mai ales, ce nu conține — XML-ul ei.

## Temeiul legal

::: ghid-temei
„r) o referire la alte facturi sau documente emise anterior, atunci când se emit mai multe facturi ori documente pentru aceeași operațiune." — Cod fiscal 227/2015, art. 319 alin. (20)

„(21) Facturile emise în sistem simplificat […] trebuie să conțină cel puțin următoarele informații: […] e) în cazul documentelor sau mesajelor tratate drept factură în conformitate cu prevederile alin. (2), o referire specifică și clară la factura inițială și la detaliile specifice care se modifică." — Cod fiscal 227/2015, art. 319 alin. (21)

„Articolul 330 Corectarea facturilor (1) […] b) […] se emite o nouă factură care trebuie să cuprindă, pe de o parte, informațiile din factura inițială, numărul și data facturii corectate, valorile cu semnul minus […]" — Cod fiscal 227/2015, art. 330
:::

## Ce se transmite, de fapt

Când se stornează sau se corectează o factură, sistemul generează un document nou, cu numărul lui propriu, prin exact același mecanism de creare ca orice factură obișnuită. Acest document nou intră în fluxul standard de emitere/transmitere la SPV — nu există o categorie separată de „document de corecție" cu reguli proprii de transmitere.

Legea cere însă ca acest document să poarte, pe el, o referință clară la factura pe care o corectează — fie numărul și data facturii corectate (art. 330 alin. 1 lit. b), fie o referire specifică (art. 319 alin. 21 lit. e). Standardul tehnic al e-Factura are un câmp dedicat pentru exact această referință (de tipul BillingReference/InvoiceDocumentReference, cunoscut și ca BT-25 în schema europeană).

Verificat direct în codul care construiește documentele de storno: acest câmp nu e populat. Singurul indiciu vizibil pe document e prefixul text „STORNO: " în descrierea fiecărei linii — util pentru un cititor uman, dar fără valoare de referință structurată pentru un sistem care parsează XML-ul.

## Ce se greșește în practică

- Se transmite factura de corecție crezând că SPV va „recunoaște" automat legătura cu originalul din câmpurile standard — câmpul de referință rămâne needle.
- Se verifică doar dacă factura a fost acceptată de SPV, fără a verifica și dacă XML-ul conține referința la factura inițială, atunci când aceasta contează pentru documentarea corecției.
- Se ignoră faptul că, tehnic, factura de corecție e o factură nouă, independentă — trebuie retrimisă clientului separat, nu doar „atașată" facturii vechi.
- Nu se ține o evidență manuală, paralelă, a corespondenței număr-la-număr între facturile originale și cele de corecție, în absența referinței structurate din XML.

## Ce face iConta.eu

Documentul de corecție (generat prin `storneaza()`) e creat prin același mecanism ca orice factură emisă — număr nou rezervat din aceeași serie, linii construite din datele originalului (negate, cu descrierea prefixată „STORNO: "), apoi trimis prin fluxul standard de emitere/transmitere. Legătura cu factura originală se păstrează doar ca o coloană internă în baza de date (`storno_din_id`). Verificat prin căutare directă în codul care generează structura de e-Factura: nu există nicio generare de BillingReference, InvoiceDocumentReference sau echivalentul BT-25. Factura de corecție se transmite deci la SPV ca document independent, fără referință structurată către factura inițială.

[iConta.eu](/)
