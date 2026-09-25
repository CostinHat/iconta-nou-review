---
title: "Care este diferența dintre verificarea documentară și inspecția fiscală?"
description: "Cum diferă verificarea documentară de inspecția fiscală, potrivit Codului de procedură fiscală — obiect, procedură și efecte."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Care este diferența dintre verificarea documentară și inspecția fiscală?

Sunt două proceduri distincte ale Codului de procedură fiscală, cu întindere și formalism diferite. Verificarea documentară e o analiză „de birou", pe baza documentelor deja existente la dosarul fiscal, fără prezența fizică a contribuabilului. Inspecția fiscală e o procedură mai amplă, cu aviz prealabil, desfășurată de regulă la sediul contribuabilului, care poate examina orice stare de fapt relevantă pentru impozitare.

## Temeiul legal

::: ghid-temei
„(1) Pentru stabilirea corectă a situației fiscale a contribuabilului/plătitorului, organul fiscal poate proceda la o verificare documentară.
(2) Verificarea documentară constă în efectuarea unei analize de coerență a situației fiscale a contribuabilului/plătitorului, pe baza documentelor existente la dosarul fiscal al contribuabilului/plătitorului, precum și pe baza oricăror informații și documente transmise de terți sau deținute de organul fiscal, care au relevanță pentru determinarea situației fiscale.
(3) Verificarea documentară se efectuează de către organele de inspecție fiscală, organele de control antifraudă fiscală și organele fiscale competente să exercite verificarea situației fiscale personale [...]."
— Legea 207/2015 privind Codul de procedură fiscală, art. 148 alin. (1)-(3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Comparativ, inspecția fiscală:

::: ghid-temei
„(5) Inspecția fiscală are în vedere examinarea tuturor stărilor de fapt și raporturile juridice care sunt relevante pentru impozitare sau verificarea modului de respectare a altor obligații prevăzute de legislația fiscală și contabilă.
(4) La începerea inspecției fiscale, organul de inspecție fiscală trebuie să prezinte contribuabilului/plătitorului legitimația de inspecție și ordinul de serviciu semnat de conducătorul organului de inspecție fiscală [...]. Începerea inspecției fiscale trebuie consemnată în registrul unic de control [...] și inspecția fiscală se desfășoară în spațiile de lucru ale contribuabilului/plătitorului."
— Legea 207/2015 privind Codul de procedură fiscală, art. 118 alin. (4) și (5) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- **Obiectul**: verificarea documentară e o analiză de coerență pe baza documentelor deja existente la organul fiscal (dosar fiscal, informații de la terți); inspecția fiscală examinează toate stările de fapt și raporturile juridice relevante, putând implica investigații la sediul contribuabilului.
- **Anunțarea**: inspecția fiscală se anunță printr-un aviz scris, cu 15 sau 30 de zile înainte, după caz (art. 122); verificarea documentară nu are un aviz echivalent — se face pe baza a ceea ce organul fiscal deține deja.
- **Prezența**: inspecția fiscală se desfășoară de regulă la spațiile de lucru ale contribuabilului, cu prezentarea legitimației și a ordinului de serviciu; verificarea documentară nu presupune deplasare la contribuabil.
- **Cine o efectuează**: verificarea documentară poate fi făcută atât de organele de inspecție fiscală, cât și de organele de control antifraudă și de cele competente pentru verificarea situației fiscale personale — o sferă mai largă de organe decât cea specifică inspecției.
- **Termenul de efectuare**: verificarea documentară se efectuează în cadrul termenului de prescripție a dreptului de a stabili creanțe fiscale, iar organul fiscal poate emite decizie de impunere ori de câte ori stabilește sau modifică baza de impozitare, fie prin verificare documentară, fie prin inspecție fiscală.

## Ce se greșește în practică

- Se tratează o notificare de verificare documentară ca și cum ar fi începutul unei inspecții fiscale complete, cu toate garanțiile procedurale aferente (aviz cu termen, prezentare de legitimație) — verificarea documentară nu are aceleași formalități.
- Se ignoră o solicitare de clarificări venită în cadrul verificării documentare, considerând-o „mai puțin oficială" decât o inspecție — rezultatul verificării documentare poate duce totuși la o decizie de impunere, exact ca inspecția.
- Se confundă „rezerva verificării ulterioare" (care se anulează la finalul unei inspecții fiscale sau verificări a situației fiscale personale) cu efectele verificării documentare, care are reguli proprii la art. 149.
- Se presupune că verificarea documentară exclude o inspecție fiscală ulterioară pe aceeași perioadă — cele două proceduri au scopuri și sfere diferite și pot coexista, fiecare cu procedura ei.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu distinge în aplicație** între cele două proceduri și nu are o funcție dedicată vreuneia dintre ele. Ecranul de „control fiscal" din aplicație (`control_fiscal_api.py`) e o funcție internă de reconciliere a declarațiilor firmei (compară D112/D300/D390 cu ce ar trebui depus), diferită atât de verificarea documentară, cât și de inspecția fiscală ANAF — numele coincide, dar conceptul e altul. Gestionarea efectivă a unei verificări documentare sau a unei inspecții fiscale reale rămâne, în acest moment, în afara aplicației.

[iConta.eu](/)
