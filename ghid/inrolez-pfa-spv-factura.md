---
title: "Cum înrolez un PFA în SPV pentru e-Factura?"
description: "PFA-urile intră sub aceeași obligație de înrolare electronică în SPV ca firmele, potrivit Codului de procedură fiscală, cu identificare prin certificat calificat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum înrolez un PFA în SPV pentru e-Factura?

Un PFA nu este scutit de obligația de comunicare electronică cu ANAF doar pentru că este persoană fizică — legea îl tratează, în acest sens, la fel ca o societate: dacă desfășoară o activitate economică independentă, trebuie să fie înrolat în SPV și să se identifice cu certificat calificat.

## Temeiul legal

::: ghid-temei
„Prin excepţie de la alin. (1), contribuabilii/plătitorii persoane juridice, asocieri şi alte entităţi fără personalitate juridică, precum şi persoane fizice care desfăşoară o profesie liberală sau exercită o activitate economică în mod independent în una dintre formele prevăzute de Ordonanţa de urgenţă a Guvernului nr. 44/2008 privind desfăşurarea activităţilor economice de către persoanele fizice autorizate, întreprinderile individuale şi întreprinderile familiale [...] sunt obligaţi să transmită organului fiscal central documente de natura celor prevăzute la alin. (1) prin mijloace electronice de transmitere la distanţă în condiţiile prezentului articol, respectiv prin înrolarea în sistemul de comunicare electronică dezvoltat de Ministerul Finanţelor/A.N.A.F."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 79 alin. (1^1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Legea numește explicit PFA-urile (prin trimiterea la OUG 44/2008) printre categoriile obligate:

- Un PFA, la fel ca un întreprinzător individual sau o întreprindere familială, **este obligat**, nu doar îndreptățit, să comunice cu ANAF prin mijloace electronice, adică prin înrolarea în sistemul dezvoltat de Ministerul Finanțelor/ANAF.
- Identificarea se face **numai cu certificat calificat** (art. 80 alin. (1) lit. a) din aceeași lege) — nu cu credențiale simple de tip utilizator/parolă, care sunt permise doar persoanelor fizice fără activitate economică.
- Faptul că PFA este la normă de venit sau în sistem real de impunere nu schimbă această obligație — criteriul legii este desfășurarea unei activități economice independente, nu modul de determinare a venitului impozabil.

## Ce se greșește în practică

- Se presupune că un PFA mic, cu cifră de afaceri redusă, este scutit de înrolarea în SPV — legea nu face nicio distincție de mărime pentru această obligație.
- Se încearcă înrolarea cu certificatul digital personal, obținut pentru alte scopuri (semnătură pe documente civile), fără să se verifice că este de tip calificat, condiție cerută expres de art. 80.
- Se amână obținerea certificatului până la prima factură care ar trebui trimisă prin RO e-Factura, deși obligația de comunicare electronică cu ANAF nu depinde de momentul emiterii unei facturi.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu realizează înrolarea inițială a PFA-ului în SPV** — acest pas se face de titular, direct pe portalul ANAF, cu certificatul digital calificat propriu. Ulterior, aplicația pune la dispoziție conectorul OAuth2 (`core/spv_conector.py`), prin care contul SPV al PFA-ului poate fi legat de iConta.eu pentru trimiterea și primirea facturilor electronice. Obținerea certificatului și crearea contului SPV rămân, la acest moment, pași din afara aplicației.

[iConta.eu](/)
