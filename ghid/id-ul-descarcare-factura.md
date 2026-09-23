---
title: "Ce este ID-ul de descărcare din e-Factura?"
description: ID-ul de descărcare (id_descarcare) este identificatorul ANAF folosit pentru a prelua recipisa/XML-ul semnat al unei facturi din SPV — nu are legătură cu descărcarea gestiunii (ieșirea mărfii din stoc).
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce este ID-ul de descărcare din e-Factura?

Atenție la o coincidență de termeni: "descărcare" apare atât în "descărcarea gestiunii" (ieșirea mărfii din stoc, la vânzare), cât și în "id de descărcare" din protocolul ANAF e-Factura. Sunt două lucruri complet diferite. Dacă ați ajuns aici căutând informații despre descărcarea gestiunii la vânzarea mărfurilor, răspunsul e în alt ghid — aici explicăm strict ID-ul de descărcare din e-Factura.

ID-ul de descărcare (`id_descarcare`) este un identificator tehnic returnat de ANAF în răspunsul interogării de stadiu a unei trimiteri prin sistemul RO e-Factura (endpoint-ul `/stareMesaj`). Acest identificator se folosește apoi într-o a doua interogare, către endpoint-ul de descărcare al ANAF, pentru a prelua efectiv fișierul cu recipisa sau XML-ul semnat al facturii — adică dovada rezultatului trimiterii (acceptare, cu semnătura electronică a Ministerului Finanțelor, sau respingere, cu motivul).

Este diferit de indexul de încărcare (`index_incarcare`), care este identificatorul primit imediat la trimiterea/upload-ul facturii în SPV. Cele două formează, împreună, ciclul de viață al unei trimiteri prin e-Factura: mai întâi indexul de încărcare (la trimitere), apoi, la interogarea stadiului, id-ul de descărcare (folosit pentru a prelua rezultatul final).

## Temeiul legal

::: ghid-temei
"În situaţia în care factura electronică transmisă respectă structura prevăzută la alin. (1), se aplică semnătura electronică a Ministerului Finanţelor şi se comunică de îndată destinatarului. Aplicarea semnăturii electronice a Ministerului Finanţelor atestă primirea acesteia în sistemul naţional privind factura electronică RO e-Factura."
— OUG 120/2021, art. 4 alin. (4)
:::

Legea nu numește explicit "id de descărcare" — acesta este identificatorul tehnic prin care se preia, la interogare, chiar dovada aplicării semnăturii electronice a Ministerului Finanțelor descrisă mai sus (fișierul-recipisă), respectiv motivul respingerii, dacă e cazul.

## Ce se greșește în practică

- Se confundă cu "descărcarea de gestiune" (ieșirea mărfii din stoc la vânzare) — sunt concepte fără nicio legătură, provenite din module diferite ale aplicației.
- Se caută id-ul de descărcare imediat după trimiterea facturii — el nu există încă în acel moment; apare abia la interogarea de stadiu, după ce ANAF a produs un verdict (acceptare sau respingere).
- Se presupune că id-ul de descărcare e același cu indexul de încărcare — sunt două identificatoare distincte, cu roluri diferite în ciclul trimiterii.

## Ce face iConta.eu

iConta.eu gestionează automat, intern, ambele identificatoare ale unei trimiteri e-Factura: reține indexul de încărcare la trimitere și, la interogarea periodică a stadiului, preia și folosește id-ul de descărcare pentru a obține recipisa sau motivul respingerii. Această folosire e comună fluxului de urmărire a facturilor emise și celui de primire a facturilor de la furnizori prin SPV — este același mecanism tehnic, reutilizat pentru ambele direcții.

Menționăm onest: acest identificator este strict tehnic, intern fluxului e-Factura, și nu are nicio legătură cu descărcarea gestiunii — dacă întrebarea reală privește ieșirea mărfii din stoc la o vânzare, răspunsul corect se găsește în ghidurile despre descărcarea gestiunii, nu în cele despre e-Factura.

[iConta.eu](/)
