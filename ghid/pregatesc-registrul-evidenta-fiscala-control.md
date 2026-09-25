---
title: "Cum pregătesc registrul de evidență fiscală pentru control?"
description: "Registrul de evidență fiscală e un document intern obligatoriu, cu conținut diferit pentru firmele la profit față de persoanele fizice, care se prezintă la control, nu se depune periodic."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum pregătesc registrul de evidență fiscală pentru control?

Registrul de evidență fiscală e unul dintre documentele pe care organul de inspecție fiscală îl cere aproape întotdeauna la un control, dar el nu se depune niciodată la ANAF în mod curent — e un document intern, ținut de contribuabil și prezentat doar atunci când e solicitat. Confuzia vine adesea din faptul că există, de fapt, **două registre distincte**, cu temeiuri și conținut diferite, în funcție de tipul contribuabilului.

## Temeiul legal

::: ghid-temei
„În scopul determinării rezultatului fiscal, contribuabilii sunt obligați să evidențieze în registrul de evidență fiscală veniturile impozabile înregistrate într-un an fiscal, potrivit alin. (1), precum și cheltuielile efectuate în scopul desfășurării activității economice, în același an fiscal, inclusiv cele reglementate prin acte normative în vigoare, potrivit art. 25."
— Legea nr. 227/2015 privind Codul fiscal, art. 19 alin. (7) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Pentru **contribuabilii plătitori de impozit pe profit**, registrul se completează pe baza art. 19 din Codul fiscal, cu conținutul detaliat integral în normele de aplicare (HG nr. 1/2016), fără a fi nevoie de un formular separat aprobat prin ordin.
- Pentru **persoanele fizice** care determină venitul net în sistem real (activități independente), obligația e prevăzută la art. 68 alin. (8)-(9) din Codul fiscal, iar modelul propriu-zis e aprobat prin OMFP nr. 3254/2017.
- Registrul se totalizează pe trimestru și/sau an fiscal și evidențiază veniturile și cheltuielile pe natura lor economică.
- La control, inspectorii verifică dacă sumele din registru corespund cu cele din declarațiile fiscale depuse (D101/D100) și cu evidența contabilă.

## Ce se greșește în practică

- Se crede că registrul trebuie depus periodic la ANAF, la fel ca o declarație — de fapt el rămâne la sediul contribuabilului și se prezintă doar la cerere.
- Se confundă cele două variante ale registrului (profit vs. persoane fizice), care au temei legal, structură și mod de completare diferite.
- Registrul se completează în grabă, chiar înainte de control, în loc să fie actualizat pe măsură ce se desfășoară activitatea — ceea ce crește riscul de sume care nu se reconciliază cu declarațiile deja depuse.

## Ce face iConta.eu

Verificarea codului sursă arată că iConta.eu are un modul dedicat (`registru_evidenta_fiscala`) care tratează explicit cele **două registre ca fiind distincte**: varianta pentru impozit pe profit se derivă din sursele deja existente în aplicație (declarația D101 și evidența contabilă), în timp ce varianta pentru persoane fizice urmează structura din OMFP 3254/2017. Aplicația construiește registrul din date deja introduse, astfel încât utilizatorul nu trebuie să îl completeze manual de la zero înainte de un control.

[iConta.eu](/)
