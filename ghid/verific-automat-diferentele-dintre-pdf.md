---
title: "Cum verific automat diferențele dintre PDF și XML-ul e-Factura?"
description: "Ce spune legea despre structura obligatorie a facturii electronice RO e-Factura și de ce fișierul XML semnat, nu PDF-ul vizualizat, este exemplarul original."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific automat diferențele dintre PDF și XML-ul e-Factura?

PDF-ul unei facturi RO e-Factura e doar o reprezentare vizuală generată dintr-un fișier XML — și legea spune explicit care dintre cele două este documentul cu valoare juridică. O diferență între ele nu e o chestiune de gust vizual, ci un indiciu că generarea PDF-ului a folosit alte date decât cele transmise efectiv la ANAF.

## Temeiul legal

::: ghid-temei
„(4) În situaţia în care factura electronică transmisă respectă structura prevăzută la alin. (1), se aplică semnătura electronică a Ministerului Finanţelor şi se comunică de îndată destinatarului. Aplicarea semnăturii electronice a Ministerului Finanţelor atestă primirea acesteia în sistemul naţional privind factura electronică RO e-Factura.
(5) În situaţia în care factura electronică transmisă nu respectă structura prevăzută la alin. (1), emitentul primeşte mesaj cu erorile identificate. [...]
(6) Exemplarul original al facturii electronice se consideră fişierul de tip XML însoţit de semnătura electronică a Ministerului Finanţelor."
— OUG nr. 120/2021 privind Sistemul naţional privind factura electronică RO e-Factura, art. 4 alin. (4)-(6) (sursă: anaf_surse/oug_120_2021.txt)
:::

Ce rezultă din articol pentru verificarea practică:

- **Exemplarul original e XML-ul semnat**, nu PDF-ul. Orice viewer sau soft de contabilitate care generează un PDF din XML face o traducere — dacă traducerea are un bug, PDF-ul poate arăta o valoare diferită de cea din XML fără ca nimeni să observe fără o comparație directă.
- Structura pe care XML-ul trebuie să o respecte e definită la art. 4 alin. (1): standardul european SR EN 16931-1 și specificațiile tehnice naționale RO_CIUS.
- Singurul mod „automat" de a verifica diferențele dintre PDF și XML e, deci, să nu compari vizual cele două documente, ci să extragi din XML aceleași câmpuri (bază, TVA, total, CIF furnizor/client, linii de factură) și să le compari programatic cu ce apare în PDF — sau, mai simplu, să te bazezi exclusiv pe datele din XML, tratând PDF-ul ca pe o simplă imagine de referință.

## Ce se greșește în practică

- Se validează o factură vizual, în PDF, și se consideră implicit că XML-ul din spate e corect — dar dacă generatorul de PDF are o eroare de rotunjire sau de mapare a câmpurilor, discrepanța nu se vede decât comparând sursa.
- Se arhivează doar PDF-ul primit prin e-mail, fără XML-ul original descărcat din sistemul RO e-Factura — ceea ce contravine art. 4 alin. (6), care spune explicit că documentul original e XML-ul.
- Se ignoră mesajele de eroare de structură (art. 4 alin. (5)) primite la o transmitere respinsă, presupunându-se că factura „a plecat" doar pentru că a fost generat un PDF local.

## Ce face iConta.eu

La trimiterea unei facturi prin RO e-Factura, iConta.eu construiește XML-ul din datele facturii și îl trece printr-o poartă de validare pe structura ANAF **înainte** de a face upload-ul efectiv — dacă validarea eșuează, factura nu se trimite. Așa se elimină la sursă riscul unei divergențe: nu se transmite un XML care nu respectă structura oficială. Aplicația nu are însă, la momentul acestui ghid, un instrument dedicat de comparare automată câmp-cu-câmp între un PDF încărcat manual și XML-ul corespunzător — verificarea unei facturi primite de la un terț, unde PDF-ul și XML-ul ar putea fi generate independent, rămâne manuală.

[iConta.eu](/)
