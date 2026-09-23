---
title: Cum se transmite evidența mijloacelor fixe la schimbarea contabilului?
description: Registrele de contabilitate rămân, prin lege, în răspunderea firmei, nu a contabilului — iar iConta.eu oferă un export complet al datelor, inclusiv registrul de mijloace fixe, prin arhiva de portabilitate a cabinetului.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se transmite evidența mijloacelor fixe la schimbarea contabilului?

Registrul de mijloace fixe nu aparține contabilului care l-a ținut, ci firmei — obligația de a-l păstra și de a-l putea prezenta revine entității, indiferent câți contabili sau ce aplicații s-au succedat de-a lungul timpului.

## Temeiul legal

::: ghid-temei
„Registrele de contabilitate obligatorii și documentele justificative care stau la baza înregistrărilor în contabilitatea financiară se păstrează în arhiva persoanelor prevăzute la art. 1 timp de 5 ani calculați de la data de 1 iulie a anului următor celui încheierii exercițiului financiar în care au fost întocmite, inclusiv pentru statele de salarii."
— Legea nr. 82/1991, art. 25
:::

Obligația de păstrare (art. 25) e a firmei, nu a persoanei care a ținut contabilitatea la un moment dat — de aceea, la schimbarea contabilului sau a aplicației folosite, datele trebuie să poată fi extrase și predate integral, nu doar rezumate manual. Nu am identificat, în sursele verificate, o normă separată care să descrie procedura exactă de predare-primire a evidenței contabile între un contabil și succesorul lui — mecanismul concret ține de contractul de servicii de contabilitate și de instrumentele aplicației folosite, nu de un text legal dedicat.

## Ce se greșește în practică

- Se presupune că „predarea gestiunii" înseamnă doar un rezumat pe hârtie sau un extras din ecran, nu datele structurate propriu-zise — un contabil nou (sau alt program) are nevoie de câmpuri complete (cod, denumire, valoare de intrare, valoare reziduală, durată, dată PIF, metodă, conturi de imobilizare și de amortizare), nu doar de o listă vizuală.
- Se lasă transmiterea evidenței la latitudinea fostului contabil, fără ca firma să verifice explicit că a primit o copie completă a datelor înainte de a schimba furnizorul de servicii.
- Se confundă exportul de rapoarte curente (balanțe, declarații depuse) cu exportul integral al registrelor — cel de-al doilea trebuie să includă și date structurale, precum registrul de mijloace fixe, nu doar cifre de sinteză.

## Ce face iConta.eu

Registrul de mijloace fixe nu are un buton dedicat de export separat — ecranul „Firmă > Mijloace fixe" e construit pentru consultare și pentru acțiunile curente (casare, reevaluare), nu pentru descărcarea unui fișier. Datele complete ale firmei, inclusiv toate tabelele tenantului (deci și registrul de mijloace fixe), pot fi descărcate integral, în format JSON per tabelă, prin arhiva de portabilitate din „Setări > Datele cabinetului (GDPR) > Descarcă arhiva cabinetului" — un mecanism general de portabilitate a datelor, nu unul specific mijloacelor fixe. Dacă noul contabil preia evidența în alt program (sau într-o altă firmă din iConta.eu), câmpurile cerute de funcția de import/migrare a aplicației (cod, denumire, valoare de intrare, valoare reziduală, durată în luni, dată PIF, metodă, cont de imobilizare, cont de amortizare) arată exact structura minimă de date necesară pentru o predare completă.

[iConta.eu](/)
