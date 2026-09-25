---
title: "Pot trimite PDF-ul clientului înainte de validarea în e-Factura?"
description: "Ce document contează legal ca factură transmisă, atunci când factura circulă și prin RO e-Factura, și de ce un PDF trimis separat nu ține loc de comunicare oficială."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Pot trimite PDF-ul clientului înainte de validarea în e-Factura?

Puteți trimite clientului un PDF sau o copie a facturii oricând, ca informare — dar din punct de vedere legal, acel document nu este „factura comunicată". Data comunicării oficiale e stabilită exclusiv de momentul în care factura devine disponibilă în sistemul RO e-Factura.

## Temeiul legal

::: ghid-temei
„(6) Exemplarul original al facturii electronice se consideră fișierul de tip XML însoțit de semnătura electronică a Ministerului Finanțelor.
(7) Data comunicării facturii electronice către destinatar se consideră data la care factura electronică este disponibilă acestuia pentru descărcare din sistemul național privind factura electronică RO e-Factura. Destinatarul este notificat cu privire la facturile electronice primite în sistemul național privind factura electronică RO e-Factura [...]. Data comunicării este accesibilă în sistem și emitentului facturii electronice."
— OUG 120/2021, art. 4 alin. (6) și (7) (sursă: anaf_surse/oug_120_2021.txt)
:::

Ce înseamnă practic:

- **Originalul legal e fișierul XML semnat electronic de Ministerul Finanțelor**, nu PDF-ul generat de aplicația contabilă și nici cel trimis pe e-mail clientului — acesta din urmă e cel mult o copie informativă.
- **Data comunicării către client** e stabilită de sistem: momentul din care factura devine disponibilă pentru descărcare în RO e-Factura, indiferent când a fost trimis un PDF separat pe e-mail sau prin altă cale.
- Trimiterea unui PDF **înainte** ca factura să fie validată și disponibilă în sistem nu produce niciun efect juridic de comunicare — dacă factura conține erori și e respinsă la validare (art. 4 alin. (5)), clientul ar primi un document care nu corespunde cu ce va ajunge, în final, prin sistemul oficial.
- Dacă factura electronică respectă structura cerută, se aplică semnătura electronică a Ministerului Finanțelor și **se comunică de îndată destinatarului** — procesul e practic automat, deci trimiterea manuală a unui PDF în avans nu aduce, de regulă, un avantaj de timp semnificativ.
- O factură deja comunicată destinatarului prin sistem **nu se mai poate returna** — orice corecție ulterioară trebuie făcută conform art. 330 din Codul fiscal și retransmisă prin același sistem RO e-Factura, nu prin trimiterea unui PDF corectat separat.

## Ce se greșește în practică

- Se trimite clientului PDF-ul facturii imediat ce e generată în contabilitate, înainte de validarea prin RO e-Factura, iar dacă factura e respinsă la validare, clientul rămâne cu un document care nu mai corespunde cu factura oficială transmisă ulterior.
- Se consideră data trimiterii PDF-ului drept „data facturării" pentru evidențele proprii ale clientului, deși legal data comunicării e cea din sistemul RO e-Factura.
- Se încearcă „retragerea" unei facturi deja comunicate prin trimiterea unui PDF anulat — legal, o factură comunicată nu se poate returna în sistem, corecția trebuie făcută conform art. 330 Cod fiscal.

## Ce face iConta.eu

iConta.eu generează factura, o transmite prin conectorul propriu către sistemul RO e-Factura (upload XML, urmărirea stării mesajului — validat, respins sau în procesare) și oferă și un PDF al facturii pentru uz intern sau pentru trimitere informativă către client. La data acestui ghid, aplicația **nu blochează** generarea sau trimiterea separată a PDF-ului înainte de confirmarea validării în e-Factura — decizia de a trimite clientului PDF-ul înainte sau după validare rămâne a contabilului/utilizatorului, cu mențiunea legală de mai sus: doar XML-ul validat și semnat de Ministerul Finanțelor are valoare de original.

[iConta.eu](/)
