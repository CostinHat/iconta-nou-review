---
title: Cum se mapează planul de conturi în SAF-T?
description: Planul de conturi se mapează pe baza normei contabile a firmei (societăți comerciale, IFRS, bănci, ONG etc.), fiecare cu propriul nomenclator oficial ANAF, iar AccountID trebuie să fie contul sintetic numeric întreg, nu contul analitic.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se mapează planul de conturi în SAF-T?

Secțiunea `GeneralLedgerAccounts` din D406 nu preia orice cont din balanța firmei, ci doar conturile care există în nomenclatorul oficial corespunzător normei contabile aplicabile. Alegerea normei greșite sau folosirea contului analitic în loc de cel sintetic sunt printre cele mai frecvente cauze de respingere la validare.

## Temeiul legal

::: ghid-temei
"NOTĂ: Secţiunea "Taxonomies" (Taxonomii) nu va trebui raportată în D406."
(opanaf_1783_2021_saft_d406.txt, Anexa 1, pct. 5, nota de sub tabel)

"În această subsecţiune se raportează atât contul analitic folosit de către
contribuabil/plătitor pentru înregistrarea tranzacţiilor în sistemul contabil conform
planului de conturi aplicabil conform legislaţiei româneşti (AccountID), cât şi contul
contabil pe baza standardului utilizat în principal de către contribuabil/plătitor în
ERP-ul intern (StandardAccountID, fiind un câmp opţional)."
(opanaf_1783_2021_saft_d406.txt, Anexa 1, pct. 5)
:::

## Norma contabilă determină nomenclatorul

Fiecare firmă are o normă contabilă declarată (`baza_contabila`): societăți comerciale (OMFP 1802/2014), IFRS, bancar, asigurări, ONG, sau reglementările specifice (Norma 39, Norma 36, Norma 14, IFN). Fiecare normă are propriul nomenclator oficial de conturi acceptate — extras direct din validatorul oficial ANAF (DUK), nu un plan inventat de aplicație.

Un cont din balanța firmei este raportat în `GeneralLedgerAccounts` doar dacă apare în nomenclatorul normei declarate. Un cont care nu se regăsește acolo este exclus din raportare, chiar dacă are mișcări reale în balanță.

::: ghid-exemplu
O firmă cu norma contabilă implicită "societăți comerciale" (OMFP 1802/2014) are în balanță conturile 731-738 (venituri specifice ONG-urilor, OMFP 3103/2017). Aceste conturi nu există în nomenclatorul planului de conturi pentru societăți comerciale, deci sunt excluse din `GeneralLedgerAccounts` — dacă ar fi incluse, validatorul oficial le-ar respinge cu eroarea "ID-ul contului [731] trebuie să se găsească în planul de conturi".
:::

Un al doilea aspect important: `AccountID` trebuie să fie un număr întreg — contul sintetic (rădăcina), de exemplu `401`, nu contul analitic `401.05`. Analiticele pe partener (client/furnizor) se transmit separat, prin secțiunile `Customers`/`Suppliers`, nu prin conturi cu punct în `GeneralLedgerAccounts` — un cont analitic transmis direct acolo este respins de validator cu eroarea "număr întreg eronat".

## Ce se greșește în practică

- Se transmit conturi analitice (cu punct, ex. `401.05`) direct în `GeneralLedgerAccounts`, în loc de rădăcina sintetică.
- Se folosește norma contabilă implicită (societăți comerciale) pentru o firmă cu contabilitate specifică (ONG, bancă, asigurări), ceea ce duce la respingerea conturilor specifice acelui domeniu.
- Se presupune că toate conturile din balanța firmei sunt raportate automat, indiferent de norma declarată — de fapt sunt filtrate pe nomenclatorul oficial al normei.
- Se raportează secțiunea "Taxonomies", deși norma spune explicit că aceasta nu trebuie inclusă în D406.

## Ce face iConta.eu

Maparea normă→nomenclator este automată, prin `PLAN_NOMENCLATOR` din motorul D406: fiecare normă contabilă (A — societăți comerciale, IFRS, BANK, INSURANCE, ONG, NORMA39, NORMA36, NORMA14, IFN) are cheia proprie citită direct din nomenclatorul oficial extras din validatorul ANAF (DUK), nu dintr-un plan inventat de aplicație. Norma implicită folosită este `"A"` (societăți comerciale, OMFP 1802/2014). La construirea declarației, conturile din balanța firmei care nu se regăsesc în nomenclatorul normei declarate sunt excluse automat din `GeneralLedgerAccounts` și colectate separat. AccountID este generat ca rădăcina sintetică numerică a contului, iar analiticele pe parteneri sunt transmise corect prin secțiunile Customers/Suppliers, nu prin conturi cu punct.

[iConta.eu](/)
