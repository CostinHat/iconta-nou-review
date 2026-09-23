---
title: Ce conturi contabile se raportează în D406?
description: D406 preia din registrul-jurnal toate conturile folosite de firmă, mapate la nomenclatorul ANAF de conturi acceptate — nu doar o selecție a lor.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce conturi contabile se raportează în D406?

D406 (SAF-T) nu este o declarație în care alegeți ce conturi să raportați — structura fișierului cere reflectarea integrală a planului de conturi folosit efectiv de firmă, în perioada raportată.

## Temeiul legal

::: ghid-temei
„MasterFiles ... Conţine date preluate din Registrul-jurnal, furnizori, clienţi, produse, stocuri, active etc." — cu subsecțiuni detaliate: GeneralLedgerAccounts (conturi, tip, solduri), Customers, Suppliers, Tax Table, UOMTable, AnalysisType Table, MovementType Table, Products, PhysicalStock, Owners, Assets. — OPANAF nr. 1783/2021, Anexa 1, pct. 4-5.
:::

Secțiunea **GeneralLedgerAccounts**, parte din MasterFiles, este cea în care se raportează conturile contabile — cu tipul lor (activ/pasiv/bifuncțional, după caz) și soldurile aferente perioadei. Aceasta este distinctă de **GeneralLedgerEntries**, secțiunea care conține înregistrările contabile propriu-zise (rulajele), nu doar lista de conturi.

Pentru ca datele să fie validabile, fiecare cont din planul de conturi al firmei trebuie să aibă un corespondent în nomenclatorul tehnic SAF-T acceptat de ANAF pentru structura XML a fișierului — nomenclator care descrie forma și codificarea acceptată, nu obligația de raportare în sine.

## Ce se greșește în practică

Cea mai frecventă greșeală este raportarea parțială — de exemplu, includerea doar a conturilor "principale" și omiterea conturilor analitice sau a celor cu rulaj redus în perioadă, pe motiv că "nu au mișcare semnificativă". Structura SAF-T nu prevede un prag de semnificație pentru includerea unui cont în GeneralLedgerAccounts.

## Ce face iConta.eu

Conform stadiului tehnic curent al generatorului (`core/d406.py`, actualizat 03.08.2026): „Header + MasterFiles + GeneralLedgerEntries complet din XSD" — secțiunea de conturi contabile (GeneralLedgerAccounts) este generată integral, automat, din planul de conturi al firmei, fără intervenție manuală de selecție. Fișierul rezultat este validat structural cu DUKIntegrator înainte de a fi considerat conform.

[iConta.eu](/)
