---
title: "e-Factura cu TVA la încasare: cum se transmite"
description: "Ce se schimbă, și ce nu se schimbă, când o firmă la TVA la încasare trece la facturarea electronică obligatorie prin RO e-Factura."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# e-Factura cu TVA la încasare: cum se transmite

Facturarea electronică obligatorie prin RO e-Factura (OUG 120/2021) nu creează un traseu separat pentru firmele înscrise la TVA la încasare. Sistemul național primește, validează și confirmă facturi după aceeași structură tehnică, indiferent de regimul de TVA al emitentului — ceea ce trebuie să se schimbe e conținutul facturii, nu canalul prin care circulă.

## Temeiul legal

::: ghid-temei
„(3) Factura electronică se transmite de către emitent în sistemul naţional privind factura electronică RO e-Factura. (4) În situaţia în care factura electronică transmisă respectă structura prevăzută la alin. (1), se aplică semnătura electronică a Ministerului Finanţelor şi se comunică de îndată destinatarului. Aplicarea semnăturii electronice a Ministerului Finanţelor atestă primirea acesteia în sistemul naţional privind factura electronică RO e-Factura."
— OUG nr. 120/2021, art. 4 alin. (3)-(4) (sursă: [OUG nr. 120/2021 privind sistemul național RO e-Factura](https://legislatie.just.ro/Public/DetaliiDocument/247243))

„Elementele facturii [...] p) în cazul în care exigibilitatea TVA intervine la data încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, mențiunea «TVA la încasare»."
— Codul fiscal, art. 319 alin. (20) lit. p) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

- Structura tehnică a facturii electronice (SR EN 16931-1, RO_CIUS) e aceeași pentru toți emitenții — nu există un `InvoiceTypeCode` sau o schemă separată pentru facturile emise sub TVA la încasare.
- Ce diferă e o singură cerință de conținut, prevăzută separat în Codul fiscal, nu în OUG 120/2021: mențiunea obligatorie „TVA la încasare" pe factură (art. 319 alin. 20 lit. p)), atunci când exigibilitatea taxei e legată de încasare (art. 282 alin. 3). Mențiunea nu e opțională și nu depinde de acordul cumpărătorului: ea îi spune destinatarului plătitor de TVA că dreptul lui de deducere pentru achiziția respectivă e amânat până la plata facturii către furnizor (art. 297 alin. 2).
- Momentul la care e obligatorie transmiterea electronică (art. 319 din Codul fiscal coroborat cu termenele stabilite pentru B2B) nu depinde de regimul de TVA al firmei — se aplică la fel firmelor cu TVA la încasare și celor din regimul normal.
- Exemplarul original al facturii, din punct de vedere legal, e fișierul XML semnat electronic de Ministerul Finanțelor, nu forma tipărită sau PDF trimisă separat clientului (art. 4 alin. 6).

## Ce se greșește în practică

- Se așteaptă ca trecerea la TVA la încasare să ceară o configurare tehnică separată a conexiunii la RO e-Factura (alt profil, altă autorizare OAuth) — conexiunea și autorizarea la ANAF sunt independente de regimul de TVA al firmei.
- Se presupune că sistemul RO e-Factura validează sau semnalează automat lipsa mențiunii „TVA la încasare" — validarea tehnică (schematronul FACT1) verifică structura XML, nu conținutul textual al mențiunilor fiscale obligatorii din Codul fiscal.
- Se transmite factura fără mențiune, considerând că se poate "regla ulterior" cu clientul pe altă cale — odată încărcat și semnat, XML-ul e exemplarul original al facturii; o corecție cere de regulă o factură de stornare/corecție, nu o notificare separată.
- Se pune mențiunea doar pe PDF-ul trimis pe e-mail, nu și în XML-ul încărcat în SPV — care e exemplarul original al facturii.
- Se confundă mențiunea „TVA la încasare" cu mențiunea „taxare inversă" — sunt reguli diferite, pentru situații diferite (art. 319 alin. 20 lit. p), respectiv lit. m)).
- Destinatarul primește factura cu mențiunea corectă, dar deduce TVA imediat, deși dreptul lui de deducere e amânat până la plată.
- Se ignoră faptul că întârzierea transmiterii peste termenul legal e sancționabilă contravențional, indiferent de regimul de TVA al emitentului.

## Ce face iConta.eu

iConta.eu transmite facturile prin RO e-Factura de la un capăt la altul: generează XML-ul UBL/CIUS-RO, îl validează pe schematronul oficial ANAF, îl încarcă în SPV pe baza autorizării ANAF a cabinetului și urmărește automat recipisa. Transmiterea se face la fel pentru toate firmele, indiferent de regimul lor de TVA — nu există un traseu separat pentru firmele la TVA la încasare.

Limita, spusă direct: aplicația **nu adaugă automat** mențiunea legală „TVA la încasare" în factura electronică generată, indiferent de regimul de TVA al firmei emitente. Dacă firma e înscrisă la TVA la încasare, mențiunea obligatorie de la art. 319 alin. (20) lit. p) rămâne în sarcina contabilului, care trebuie s-o adauge manual (de exemplu în descrierea unei linii sau într-un câmp de observații al facturii, dacă există) înainte de a considera obligația de facturare corect îndeplinită.

[iConta.eu](/)
