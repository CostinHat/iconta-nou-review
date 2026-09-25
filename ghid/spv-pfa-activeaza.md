---
title: "SPV pentru PFA: cum se activează"
description: "Activarea contului SPV pentru un PFA este o obligație legală de comunicare electronică cu organul fiscal, cu identificare exclusiv prin certificat calificat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# SPV pentru PFA: cum se activează

Pentru un PFA, activarea SPV nu ține de comoditate — este obligație de comunicare electronică cu ANAF, iar activarea presupune un singur ingredient obligatoriu: certificatul digital calificat.

## Temeiul legal

::: ghid-temei
„Prin excepţie de la alin. (1), contribuabilii/plătitorii persoane juridice, asocieri şi alte entităţi fără personalitate juridică, precum şi persoane fizice care desfăşoară o profesie liberală sau exercită o activitate economică în mod independent în una dintre formele prevăzute de Ordonanţa de urgenţă a Guvernului nr. 44/2008 [...] sunt obligaţi să transmită organului fiscal central documente de natura celor prevăzute la alin. (1) prin mijloace electronice de transmitere la distanţă în condiţiile prezentului articol, respectiv prin înrolarea în sistemul de comunicare electronică dezvoltat de Ministerul Finanţelor/A.N.A.F."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 79 alin. (1^1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Pentru activarea propriu-zisă, doi pași sunt esențiali, conform legii:

- **Certificatul digital calificat** al titularului PFA este condiția de identificare — art. 80 alin. (1) lit. a) din aceeași lege prevede că persoanele fizice cu activitate economică independentă „se identifică numai cu certificate calificate", spre deosebire de persoanele fizice fără activitate economică, care au și alte opțiuni.
- **Înrolarea** propriu-zisă în sistemul de comunicare electronică al Ministerului Finanțelor/ANAF se face cu acest certificat, direct pe portalul ANAF — procedura tehnică de ecran este stabilită prin ordin al președintelui ANAF, act care nu a fost identificat verbatim în sursele verificate pentru acest ghid.
- Odată activat contul, PFA-ul poate comunica electronic toate documentele relevante cu organul fiscal, iar pentru RO e-Factura, dacă intră sub incidența obligației de transmitere (B2B sau B2C), trebuie să facă separat pasul de înscriere în Registrul RO e-Factura obligatoriu.

## Ce se greșește în practică

- Se încearcă activarea SPV fără certificat calificat, cu credențiale simple — funcționează doar pentru persoanele fizice fără activitate economică, nu pentru un PFA.
- Se presupune că activarea SPV echivalează cu înscrierea automată în Registrul RO e-Factura — sunt doi pași administrativi distincți.
- Se amână activarea până când apare prima obligație de raportare, deși legea impune înrolarea ca obligație generală de comunicare, independentă de existența unei declarații concrete de depus la un moment dat.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu activează contul SPV al PFA-ului** — acest pas rămâne al titularului, direct pe portalul ANAF, cu certificatul digital calificat. După activare, aplicația oferă conectorul OAuth2 (`core/spv_conector.py`) prin care contul SPV deja activ poate fi legat de iConta.eu, pentru trimiterea și primirea facturilor electronice din interfața de facturare a aplicației.

[iConta.eu](/)
