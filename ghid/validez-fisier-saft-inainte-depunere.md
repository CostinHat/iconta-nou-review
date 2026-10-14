---
title: "Cum validez un fișier SAF-T înainte de depunere"
description: Cum se validează structural un fișier D406 înainte de depunere și ce instrument oficial verifică schema XML.
published: 2026-09-25
modified: 2026-10-13
poarta: v1
---

# Cum validez un fișier SAF-T înainte de depunere

SAF-T nu se validează cu un instrument oarecare — procedura oficială cere trecerea fișierului prin validatorul desemnat de ANAF, înainte de generarea PDF-ului semnat electronic.

## Temeiul legal

::: ghid-temei
„Pentru pregătirea şi transmiterea fişierului standard de control fiscal prin intermediul Declaraţiei informative D406 se derulează următoarele activităţi: a) generarea fişierului SAF-T în format XML de către sistemul informatic al contribuabilului/plătitorului; b) verificarea structurii fişierului XML şi a corelaţiilor dintre date prin programul informatic "Validator" pus la dispoziţie de către Agenţia Naţională de Administrare Fiscală (ANAF); c) generarea Declaraţiei informative D406 ca document electronic în format PDF cu XML ataşat (dacă acesta a îndeplinit condiţiile de verificare) semnat electronic.”
— OPANAF nr. 1783/2021, anexa nr. 3, pct. 1 (sursă: [OPANAF nr. 1783/2021 privind fișierul standard de control fiscal (SAF-T, D406)](https://legislatie.just.ro/Public/DetaliiDocument/248326))
:::

## De ce nu se poate sări peste validare

Validarea nu e opțională și nu poate fi înlocuită de o verificare vizuală a fișierului XML — schema SAF-T e complexă (patru module, zeci de câmpuri obligatorii, coduri de nomenclator), iar un fișier structural greșit e respins la depunere sau, mai rău, acceptat cu date incorecte.

În iConta.eu, validarea tehnică se face cu **DUKIntegrator** (validatorul ANAF (DUKIntegrator), apelat prin funcția „validarea”) — instrumentul de validare structurală folosit și de ANAF, apelat pentru fișierul, tipul de declarație și perioada respectivă. Există un istoric relevant aici: la un moment dat, butonul de validare din aplicație nu trimitea corect anul și luna către validator și întorcea mereu o stare intermediară („gri"), indiferent de conținutul real al fișierului — problemă identificată și reparată, cu validare confirmată „valid" pe date reale ale mai multor firme.

## Ce se greșește în practică

- Se presupune că un fișier XML care „arată bine" la o citire manuală e valid structural — validarea reală se face doar cu instrumentul oficial.
- Se ignoră mesajele de eroare ale validatorului dacă declarația tot poate fi „depusă" tehnic — o depunere cu erori structurale poate fi respinsă sau poate genera solicitări ulterioare de la ANAF.
- Se confundă validarea structurală (XSD, coduri de nomenclator) cu corectitudinea de fond a datelor — validatorul verifică forma fișierului, nu dacă cifrele reflectă realitatea contabilă.

## Ce face iConta.eu

Fiecare fișier D406 generat în iConta.eu e trecut prin DUKIntegrator înainte de a fi pus la dispoziție pentru transmitere, iar rezultatul validării e verificat explicit pentru anul, luna și tipul declarației respective — nu doar rulat generic. Bug-ul istoric legat de starea „gri" persistentă, cauzat de netransmiterea corectă a anului și lunii către validator, a fost identificat și reparat, cu confirmare pe date reale.

[iConta.eu](/)
