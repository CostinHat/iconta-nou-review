---
title: "Cum configurez casa de marcat pentru noile reguli 2026?"
description: "Ce obligații legale trebuie verificate la configurarea unei case de marcat electronice fiscale, dincolo de setările tehnice ale aparatului."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum configurez casa de marcat pentru noile reguli 2026?

„Configurarea" unei case de marcat pentru 2026 nu se rezumă la setările interne ale aparatului (cote de TVA, articole, prețuri) — legea impune și o configurare la nivel de conformitate: conectarea la distanță la sistemul ANAF de supraveghere, corectitudinea datelor din bonul fiscal și emiterea lui la fiecare vânzare.

## Temeiul legal

::: ghid-temei
„(4) În vederea realizării supravegherii și monitorizării aparatelor de marcat electronice fiscale, operatorii economici prevăzuți la art. 1 alin. (1) au obligația de a asigura conectarea la distanță a aparatelor de marcat electronice fiscale, în vederea transmiterii de date fiscale către Agenția Națională de Administrare Fiscală.
(5) Procedura de conectare a aparatelor de marcat electronice fiscale, precum și data începând cu care acestea se conectează la sistemul informatic național de supraveghere și monitorizare a datelor fiscale se aprobă prin ordin al președintelui Agenției Naționale de Administrare Fiscală."
— OUG nr. 28/1999 (republicată), art. 3^1 alin. (4), (5) (sursă: anaf_surse/oug_28_1999.html)
:::

Ce înseamnă „configurare conformă" pentru un aparat funcțional în 2026:

- **Conexiunea la distanță** trebuie activă și funcțională, astfel încât aparatul să transmită automat date fiscale către ANAF — procedura tehnică exactă (protocoale, frecvență) este stabilită prin ordin al președintelui ANAF, nu de operatorul economic.
- **Datele obligatorii de pe bonul fiscal** (denumirea și codul de identificare fiscală ale operatorului economic emitent, adresa locului de instalare, seria fiscală, data și ora emiterii etc. — art. 4 alin. (1)) trebuie configurate corect la instalare, pentru ca fiecare bon emis să fie valid.
- **Cotele de TVA** setate în aparat trebuie să corespundă cu cele efectiv aplicabile fiecărei categorii de bunuri/servicii vândute — o configurare greșită a cotelor produce discrepanțe între Raportul Z și evidența contabilă reală.
- Orice modificare relevantă (schimbare de adresă a punctului de lucru, schimbare de activitate) trebuie reflectată atât în configurarea aparatului, cât și în Registrul național ANAF, prin unitatea acreditată de service.

## Ce se greșește în practică

- Se configurează corect prețurile și articolele, dar se ignoră verificarea conexiunii la distanță la sistemul ANAF, care poate rămâne nefuncțională fără să fie sesizată imediat.
- Se folosesc cote de TVA vechi/incorecte în aparat după o modificare legislativă, ceea ce duce la bonuri fiscale cu TVA calculat greșit.
- Se presupune că actualizarea software-ului intern al casei de marcat e suficientă pentru conformitate, fără verificarea că datele de identificare de pe bon (adresă, CIF) reflectă situația curentă a operatorului economic.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu configurează sau nu comunică direct cu aparatul de marcat electronic fiscal — setările interne ale casei (cote TVA, articole, conexiunea la distanță la ANAF) se fac exclusiv prin distribuitorul/unitatea acreditată de service a aparatului. Aplicația intervine ulterior, în etapa contabilă: importă Raportul Z generat de aparat (format p7b/XML, structură OPANAF 146/2018) prin `core/amef_import.py`, extrăgând totalurile de vânzări pe modalități de plată și pe cote de TVA, pentru înregistrarea lor în contabilitate.

[iConta.eu](/)
