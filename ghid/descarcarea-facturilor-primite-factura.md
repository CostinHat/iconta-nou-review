---
title: Descărcarea facturilor primite din e-Factura
description: Privire de ansamblu asupra mecanismului complet — de la interogarea automată a ANAF la fiecare 30 de minute, până la validarea manuală care transformă ciorna într-o cheltuială contabilizată.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Descărcarea facturilor primite din e-Factura

Facturile pe care furnizorii tăi le trimit prin sistemul RO e-Factura ajung în aplicație pe un flux complet automat până la un anumit punct — apoi se opresc voit, la un pas care rămâne decizia contabilului.

## Temeiul legal

::: ghid-temei
„Factura electronică se transmite de către emitent în sistemul naţional privind factura electronică RO e-Factura."

— OUG nr. 120/2021, art. 4 alin. (3)
:::

::: ghid-temei
„Data comunicării facturii electronice către destinatar se consideră data la care factura electronică este disponibilă acestuia pentru descărcare din sistemul naţional privind factura electronică RO e-Factura. Destinatarul este notificat cu privire la facturile electronice primite (...) conform procedurii prevăzute la art. 3 alin. (4)."

— OUG nr. 120/2021, art. 4 alin. (7)
:::

Legea descrie circuitul integral: furnizorul transmite factura în sistemul național, iar din momentul în care ea devine disponibilă pentru descărcare, se consideră comunicată destinatarului. Fluxul din aplicație e construit exact pe acest al doilea moment.

## Fluxul, pas cu pas

1. **Interogarea ANAF.** La fiecare 30 de minute, un proces programat cere sistemului ANAF lista mesajelor noi de tip „factură primită”, pentru fiecare firmă al cărei cabinet are o conexiune SPV activă. Fereastra interogată acoperă ultimele 3 zile la fiecare rulare, suprapusă intenționat, ca toleranță la eventuale eșecuri intermitente.
2. **Verificarea firmei corecte.** Pentru fiecare mesaj găsit, se verifică întâi că factura a fost emisă efectiv către CIF-ul firmei respective — nu al alteia din același cabinet. Fără această verificare, un cabinet cu mai multe firme ar risca să vadă facturi ale unei firme amestecate cu ale alteia.
3. **Evitarea reimportului.** Fiecare mesaj ANAF are un identificator unic; dacă a fost deja descărcat la o rulare anterioară, nu se aduce a doua oară.
4. **Descărcarea și extragerea.** XML-ul (sau arhiva care îl conține) e descărcat și parsat automat — furnizor, număr, dată, sume, linii. Dacă parsarea reușește, factura devine „ciornă” gata de previzualizat; dacă XML-ul nu poate fi parsat corect, rămâne totuși vizibilă, ca „descărcată”, ca să nu se piardă.
5. **Validarea.** Nimic din pașii de mai sus nu creează automat o cheltuială. Doar la validarea manuală, cu contul de cheltuială confirmat sau ales explicit de contabil, factura devine o cheltuială contabilizată propriu-zisă — legată, la nevoie, de o factură deja existentă cu același număr, furnizor și dată, dacă ea a mai fost validată o dată.

## Ce se greșește în practică

- Se așteaptă ca o factură descărcată automat să apară direct printre cheltuielile firmei — de fapt rămâne ciornă, în lista de validat, până e confirmată de contabil.
- Se ignoră pentru perioade lungi lista de facturi de validat, considerând că „dacă a intrat automat, treaba e gata” — nu e, contul de cheltuială trebuie confirmat pentru fiecare.
- Se presupune că lipsa unei facturi noi înseamnă o eroare a aplicației, fără a verifica întâi conexiunea SPV a cabinetului și CUI-ul firmei — cele mai frecvente cauze reale.

## Ce face iConta.eu

Tot ce ține de aducerea facturii — interogare, verificare de firmă, evitarea reimportului, descărcare, parsare — rulează automat, la 30 de minute, fără nicio acțiune din partea contabilului. Ultimul pas, transformarea ciornei într-o cheltuială reală, rămâne manual prin decizie asumată: contul de cheltuială și deductibilitatea sunt o decizie profesională, nu ceva ce sistemul presupune singur. Aplicația nu afișează încă, într-un ecran dedicat contabilului, motivele tehnice pentru care o factură nu s-a descărcat (conexiune SPV lipsă, CUI necompletat, arhivă fără XML valid) — acestea rămân, la acest moment, de diagnosticat manual.

[iConta.eu](/)
