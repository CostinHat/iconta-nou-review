---
title: "Cum intru în SPV pentru RO e-Factura?"
description: "Cine este obligat să se înroleze în Spațiul Privat Virtual pentru a folosi RO e-Factura și ce prevede legea despre identificarea electronică."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum intru în SPV pentru RO e-Factura?

Accesul la sistemul RO e-Factura se face prin Spațiul Privat Virtual (SPV), platforma ANAF de comunicare electronică. Pentru majoritatea firmelor și PFA-urilor, înrolarea în SPV nu mai este opțională — este o obligație legală, iar identificarea se face cu certificat digital calificat, nu cu utilizator/parolă.

## Temeiul legal

::: ghid-temei
„Prin excepţie de la alin. (1), contribuabilii/plătitorii persoane juridice, asocieri şi alte entităţi fără personalitate juridică, precum şi persoane fizice care desfăşoară o profesie liberală sau exercită o activitate economică în mod independent în una dintre formele prevăzute de Ordonanţa de urgenţă a Guvernului nr. 44/2008 [...] sunt obligaţi să transmită organului fiscal central documente de natura celor prevăzute la alin. (1) prin mijloace electronice de transmitere la distanţă în condiţiile prezentului articol, respectiv prin înrolarea în sistemul de comunicare electronică dezvoltat de Ministerul Finanţelor/A.N.A.F."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 79 alin. (1^1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Din text rezultă cine trebuie să aibă cont SPV activ și cum se identifică:

- **Obligația de înrolare** privește persoanele juridice, asocierile fără personalitate juridică și persoanele fizice care desfășoară o activitate economică independentă (inclusiv PFA, în forma reglementată de OUG 44/2008) — nu este o facilitate la alegere, ci o cerință legală de comunicare cu organul fiscal.
- **Identificarea în SPV** pentru aceste categorii se face „numai cu certificate calificate" (art. 80 alin. (1) lit. a) din aceeași lege), spre deosebire de persoanele fizice fără activitate economică, care pot folosi și alte mijloace de autentificare.
- Odată înrolat, contribuabilul comunică cu ANAF prin acest canal pentru toate documentele electronice relevante, RO e-Factura fiind una dintre componentele care funcționează pe același cont SPV.

## Ce se greșește în practică

- Se confundă înrolarea în SPV cu simpla creare a unui cont — fără certificatul digital calificat, identificarea nu este validă pentru persoanele juridice și PFA.
- Se amână înrolarea până când apare prima factură de emis, deși obligația de comunicare electronică cu ANAF există independent de momentul la care firma începe efectiv să transmită facturi.
- Se presupune că înrolarea în SPV echivalează automat cu înscrierea în Registrul RO e-Factura obligatoriu — sunt pași diferiți, cu proceduri distincte stabilite prin ordin al președintelui ANAF.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu gestionează procesul de înrolare inițială în SPV** — acesta se face direct pe portalul ANAF, cu certificatul digital al firmei sau al reprezentantului. Ce face aplicația este să se conecteze, ulterior, la contul SPV deja activ: modulul de conector SPV (`core/spv_conector.py`) implementează autorizarea OAuth2 către ANAF, permițând firmei să lege iConta.eu de propriul cont SPV pentru a trimite și primi facturi electronice. Pașii de creare a contului SPV și obținerea certificatului rămân responsabilitatea contribuabilului, în afara aplicației.

[iConta.eu](/)
