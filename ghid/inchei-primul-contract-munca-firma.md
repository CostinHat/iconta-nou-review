---
title: "Cum închei primul contract de muncă în firma nouă"
description: "Ce trebuie să conțină, prin lege, un contract individual de muncă — și de ce redactarea și semnarea lui rămân integral în afara unei aplicații de contabilitate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum închei primul contract de muncă în firma nouă

Încheierea unui contract individual de muncă (CIM) e un act juridic, nu o simplă înregistrare contabilă: legea impune forma scrisă și un set minim de clauze pe care angajatorul trebuie să le comunice viitorului salariat înainte de semnare. E important să se separe clar acest pas — redactarea și semnarea contractului — de ce se întâmplă după, când datele din contract ajung introduse într-o aplicație pentru salarizare și declarații.

## Temeiul legal

::: ghid-temei
„Contractul individual de muncă se încheie în baza consimţământului părţilor, în forma scrisă, în limba română. Obligaţia de încheiere a contractului individual de muncă în forma scrisă revine angajatorului. [...] În situaţia în care contractul individual de muncă nu a fost încheiat în forma scrisă, se prezuma ca a fost încheiat pe o durată nedeterminată, iar părţile pot face dovada prevederilor contractuale şi a prestaţiilor efectuate prin orice alt mijloc de proba."
— Legea 53/2003 (Codul Muncii), art. 16 alin. (1)-(2) (sursă: anaf_surse/legea_53_2003_codul_muncii.txt)
:::

::: ghid-temei
„Anterior încheierii sau modificării contractului individual de muncă, angajatorul are obligaţia de a informa persoana care solicită angajarea ori, după caz, salariatul cu privire la clauzele generale pe care intenţionează să le înscrie în contract sau să le modifice. [...] a) identitatea părţilor; b) locul de muncă sau, în lipsa unui loc de muncă fix, posibilitatea ca salariatul sa munceasca în diverse locuri; c) sediul sau, după caz, domiciliul angajatorului; d) atribuţiile postului; e) riscurile specifice postului; f) data de la care contractul urmează să îşi producă efectele; [...]"
— Legea 53/2003 (Codul Muncii), art. 17 alin. (1)-(2) (sursă: anaf_surse/legea_53_2003_codul_muncii.txt)
:::

- Forma scrisă e obligatorie și cade în sarcina angajatorului, nu a salariatului.
- Fără formă scrisă, legea nu anulează contractul — îl prezumă pe durată nedeterminată, ceea ce poate fi exact contrariul intenției angajatorului.
- Înainte de semnare, angajatorul trebuie să informeze salariatul cu privire la clauzele esențiale: identitatea părților, locul de muncă, atribuțiile postului, riscurile specifice, data de la care contractul produce efecte, și celelalte elemente prevăzute la art. 17 alin. (2).
- Aceste elemente sunt distincte de datele pe care le cere o aplicație de salarizare (CNP, cod COR, salariu brut) — contractul e documentul juridic din care acele date se preiau, nu invers.

## Ce se greșește în practică

- Se crede că o aplicație de contabilitate „generează" sau „validează" automat contractul de muncă — nicio aplicație de evidență salarială nu redactează, nu semnează și nu arhivează CIM-ul ca document juridic.
- Se începe activitatea salariatului înainte ca informarea prealabilă (art. 17) să fi avut loc, ceea ce lasă angajatorul fără dovadă că obligația de informare a fost respectată.
- Se confundă „tip de normă" (întreagă/parțială), pe care o aplicație de salarizare îl gestionează, cu „tip de contract" (determinat/nedeterminat) și cu clauzele contractuale propriu-zise, care rămân exclusiv în documentul semnat.

## Ce face iConta.eu

iConta.eu **nu generează, nu redactează și nu validează** contractul individual de muncă ca document. Verificat direct în cod: entitatea „salariat" din funcționalitatea Salariați (CRUD) nu are niciun câmp de tip contract sau durată de contract — nici în baza de date, nici în formularele din ecranul „Stat de plată", nici în validarea de pe server. Modulul de contracte al aplicației (mail-merge din date de „parteneri") nu are nicio legătură cu salariații. Ce face concret F078: după ce contractul a fost redactat și semnat pe hârtie sau electronic, contabilul introduce în iConta.eu datele lui esențiale — CNP (validat cu cifră de control), nume, dată de angajare, tip de normă, cod COR (verificat în nomenclator) și salariu brut — iar de acolo aplicația alimentează automat statul de plată și declarația 112; identitatea salariatului ajunge la REGES-ONLINE doar printr-un pas separat, manual (butonul „Trimite în REGES"), nu automat la introducerea datelor. Actul juridic al încheierii contractului rămâne complet în afara aplicației.

[iConta.eu](/)
