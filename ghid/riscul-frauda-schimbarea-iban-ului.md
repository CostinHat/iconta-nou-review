---
title: "Riscul de fraudă prin schimbarea IBAN-ului: cum mă feresc"
description: "Nu există o lege dedicată fraudei prin schimbare de IBAN, dar obligația de document justificativ din Legea contabilității angajează răspunderea celui care aprobă o plată către un cont neverificat."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Riscul de fraudă prin schimbarea IBAN-ului: cum mă feresc

Frauda tip "schimbare de IBAN" — un e-mail aparent de la un furnizor real, care anunță un cont bancar nou, chiar înainte de scadența unei plăți mari — e o problemă practică frecventă, dar nu are, în legislația fiscală și contabilă românească, un articol dedicat care s-o reglementeze explicit. Ce există e cadrul general privind documentele justificative, care oferă totuși un punct de sprijin legal pentru procedura de verificare.

## Temeiul legal

::: ghid-temei
„(1) Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ. (2) Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz."
— Legea contabilității nr. 82/1991, art. 6 (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

**Limitarea acestui ghid**: în sursele verificate nu există o lege specială privind frauda prin schimbarea datelor de plată (un fenomen tratat, de regulă, prin proceduri interne de control, nu printr-o normă fiscală dedicată). Ce oferă art. 6 de mai sus e cadrul legal pentru procedura de apărare:

- Orice modificare a contului bancar al unui partener, folosită ca bază pentru o plată, trebuie să se sprijine pe un document justificativ — o notificare oficială, verificabilă, nu doar un e-mail necontrolat.
- **Răspunderea** pentru o plată greșit direcționată cade explicit pe cei care au întocmit, vizat și aprobat documentul care a stat la baza ei — ceea ce înseamnă că lipsa unei verificări minime (telefon la un număr cunoscut dinainte, confirmare pe alt canal decât e-mailul care a anunțat schimbarea) expune direct persoana care a aprobat plata.
- Principiul prevalenței economicului asupra juridicului (OMFP 1802/2014, pct. 57) cere ca documentele să reflecte întocmai realitatea operațiunii — un IBAN schimbat fraudulos, dacă e acceptat fără verificare, rupe tocmai această concordanță.

## Ce se greșește în practică

- Se schimbă IBAN-ul unui furnizor în evidențe direct pe baza unui e-mail, fără o verificare pe un canal independent (telefon, semnătură pe document cu antet, confirmare printr-un contact cunoscut anterior).
- Se presupune că, dacă factura și restul detaliilor par corecte, schimbarea de cont e automat legitimă — atacatorii tipici copiază exact restul documentului, schimbând doar IBAN-ul.
- Nu se păstrează un document justificativ separat pentru schimbarea de cont în sine — la un control sau litigiu ulterior, lipsa acestui document face imposibil de demonstrat că schimbarea a fost verificată corespunzător.

## Ce face iConta.eu

iConta.eu validează formatul unui IBAN introdus (structură românească, RO + 22 caractere, cifră de control corectă) atunci când e completat, de exemplu, la datele unui salariat pentru plata pe card — dar această validare confirmă doar că IBAN-ul e *valid ca format*, nu că aparține efectiv persoanei/firmei declarate. Aplicația nu are un mecanism de detectare a schimbărilor suspecte de cont bancar la parteneri sau de alertare la o modificare recentă a datelor de plată ale unui furnizor — verificarea rămâne, integral, un proces manual, în afara aplicației.

[iConta.eu](/)
