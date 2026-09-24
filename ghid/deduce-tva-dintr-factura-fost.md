---
title: Pot deduce TVA dintr-o factură care nu a fost transmisă în e-Factura?
description: Pentru operațiunile RO-RO între persoane impozabile, doar factura transmisă prin RO e-Factura e considerată factură. Fără ea în SPV, dreptul de deducere e blocat, indiferent câte exemplare pe hârtie sau PDF există.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Pot deduce TVA dintr-o factură care nu a fost transmisă în e-Factura?

Nu, cu o precizare importantă: nu ține de calitatea documentului pe care-l ai fizic (PDF, hârtie), ci de faptul că, pentru operațiunile dintre persoane impozabile stabilite în România, e considerată factură doar cea transmisă prin sistemul național RO e-Factura.

## Temeiul legal

::: ghid-temei
**Art. 4 alin. (6) din OUG nr. 120/2021**: exemplarul original al facturii electronice se consideră fișierul de tip XML însoțit de semnătura electronică a Ministerului Finanțelor.

**Art. 10 alin. (7) din OUG nr. 120/2021** (modificat prin OUG nr. 89/2025): „Termenul-limită pentru transmiterea facturilor în sistemul național privind factura electronică RO e-Factura este de 5 zile lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită pentru emiterea facturii prevăzută la art. 319 alin. (16) din Legea nr. 227/2015... Calculul termenului-limită se efectuează conform Regulamentului (CEE, Euratom) nr. 1182/71 al Consiliului din 3 iunie 1971.”
:::

## Ce înseamnă practic

PDF-ul primit pe email de la furnizor nu e „originalul" facturii — originalul e XML-ul cu semnătura electronică a Ministerului Finanțelor, care se descarcă din SPV. Dacă furnizorul nu a transmis factura prin sistem, tehnic nu ai un document care să îndeplinească definiția legală de factură pentru o operațiune RO-RO — și fără el, condiția de la art. 299 alin. (1) lit. a) (deținerea unei facturi conforme art. 319) nu e îndeplinită.

## Ce faci dacă furnizorul nu transmite

Obligația de transmitere e a furnizorului, nu a ta — nu poți transmite tu factura altcuiva. Dacă ai plătit integral la momentul livrării/prestării și factura tot nu apare în SPV după expirarea termenului legal, ai la dispoziție **formularul 800**, introdus prin Ordinul ANAF nr. 2229/2025 (Monitorul Oficial nr. 895/30.09.2025) — o notificare depusă de tine, ca beneficiar, prin care semnalezi ANAF că furnizorul nu și-a transmis factura. Furnizorul primește mesaj în SPV și obligația de a transmite factura a doua zi.

## Ce se greșește în practică

Se presupune că un PDF primit pe email, cu toate elementele unei facturi corecte, e suficient pentru deducere — nu e, dacă factura n-a fost transmisă prin sistem pentru o operațiune între persoane impozabile stabilite în România. Al doilea tip de eroare: se confundă „factura n-a intrat încă în SPV" cu „factura nu există" — de multe ori e doar o problemă de întârziere a furnizorului, rezolvabilă prin formularul 800, nu un motiv de a renunța definitiv la deducere.

## Ce face iConta.eu

Aplicația nu blochează mecanic introducerea sau deducerea unei facturi primite pe o altă cale decât SPV — nu există, în modulul de facturi sau în generarea D300, o verificare automată care refuză o factură primită dacă aceasta lipsește din e-Factura. Confruntarea dintre ce ai introdus și ce apare efectiv în SPV rămâne, la acest moment, în responsabilitatea contabilului: se recomandă verificarea facturii primite față de SPV înainte de a-i deduce TVA, iar dacă lipsește peste termen, depunerea formularului 800.

[iConta.eu](/)
