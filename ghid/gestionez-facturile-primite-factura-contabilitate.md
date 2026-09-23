---
title: "Cum gestionez facturile primite prin e-Factura în contabilitate"
description: Descărcarea și parsarea facturilor de la furnizori sunt automate, la fiecare 30 de minute — dar transformarea lor în cheltuială contabilă rămâne, prin decizie de produs, un pas manual, cu cont obligatoriu.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum gestionez facturile primite prin e-Factura în contabilitate

Facturile pe care furnizorii tăi le transmit prin RO e-Factura ajung în aplicație pe un flux automat până la un punct precis — apoi se opresc voit, la un pas care rămâne decizia contabilului. Merită înțeles unde e granița, ca să nu presupui automatizare acolo unde nu există.

## Temeiul legal

::: ghid-temei
„Factura electronică se transmite de către emitent în sistemul naţional privind factura electronică RO e-Factura." — OUG nr. 120/2021, art. 4 alin. (3).

„Exemplarul original al facturii electronice se consideră fişierul de tip XML însoţit de semnătura electronică a Ministerului Finanţelor." — OUG nr. 120/2021, art. 4 alin. (6).
:::

## Ce se întâmplă automat

Un proces programat interoghează sistemul ANAF la fiecare 30 de minute, pentru fiecare firmă al cărei cabinet are o conexiune SPV activă. Pentru fiecare mesaj nou, se verifică întâi că factura a fost emisă efectiv către CIF-ul acelei firme — un gard obligatoriu, ca un cabinet cu mai multe firme să nu vadă facturile amestecate. Fiecare mesaj ANAF are un identificator unic, verificat ca să nu fie descărcat a doua oară.

XML-ul e descărcat și parsat automat — furnizor, număr, dată, sume, linii. Dacă parsarea reușește, factura devine „ciornă", gata de previzualizat; dacă fișierul nu poate fi parsat corect, rămâne totuși vizibil, ca „descărcat", ca să nu se piardă.

## Ce rămâne manual, prin decizie asumată

Nimic din pașii de mai sus **nu creează automat o cheltuială**. Factura descărcată primește un **cont de cheltuială sugerat** — nu ales definitiv, ci propus pe baza istoricului: dacă ai mai înregistrat facturi de la același emitent, sistemul reține contul folosit atunci și îl propune din nou.

Nota contabilă efectivă se scrie doar după ce confirmi sau schimbi contul sugerat și validezi. Contul de cheltuială e **obligatoriu** la acest pas — dacă lipsește, validarea e refuzată explicit, aplicația nu completează cu un cont implicit. O factură respinsă la validare nu dispare din evidență — rămâne cu istoricul păstrat.

Motivul e de fond: alegerea contului corect, și implicit judecata asupra deductibilității, e o decizie profesională. O factură de la același furnizor poate avea, de la o lună la alta, o natură diferită — sistemul poate sugera pattern-ul anterior, dar nu poate garanta că el rămâne corect de fiecare dată.

## Ce se greșește în practică

- Se așteaptă ca o factură descărcată automat să apară direct printre cheltuielile firmei — rămâne ciornă, în lista de validat, până e confirmată.
- Se ignoră lista de facturi de validat pentru perioade lungi, considerând că „dacă a intrat automat, treaba e gata" — nu e; contul de cheltuială trebuie confirmat pentru fiecare.
- Se presupune că lipsa unei facturi noi înseamnă o eroare a aplicației, fără a verifica întâi conexiunea SPV a cabinetului și CUI-ul firmei — cele mai frecvente cauze reale.

## Ce face iConta.eu

Descărcarea, verificarea firmei corecte, evitarea reimportului și parsarea rulează automat, la 30 de minute, fără nicio acțiune din partea contabilului. Ultimul pas — transformarea ciornei într-o cheltuială reală, cu cont de deductibilitate confirmat — rămâne deliberat manual, cu cont obligatoriu la validare. Aplicația nu afișează încă, într-un ecran dedicat, motivele tehnice exacte pentru care o factură nu s-a descărcat (conexiune SPV lipsă, CUI necompletat, arhivă fără XML valid) — acestea rămân, la acest moment, de diagnosticat manual.

[iConta.eu](/)
