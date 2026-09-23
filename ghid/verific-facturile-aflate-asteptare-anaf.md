---
title: "Cum verific facturile aflate în așteptare la ANAF?"
description: Ce înseamnă "în așteptare" pentru facturile emise de firma dumneavoastră aflate în curs de validare la ANAF prin RO e-Factura, și cum sunt urmărite tehnic.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum verific facturile aflate în așteptare la ANAF?

Discuția privește facturile pe care firma dumneavoastră **le-a emis și le-a trimis** către ANAF prin RO e-Factura și care nu au primit încă un verdict definitiv — nu facturile primite de la furnizori, care sunt urmărite printr-un flux separat.

## Temeiul legal

::: ghid-temei
"În situaţia în care factura electronică transmisă respectă structura prevăzută la alin. (1), se aplică semnătura electronică a Ministerului Finanţelor şi se comunică de îndată destinatarului. Aplicarea semnăturii electronice a Ministerului Finanţelor atestă primirea acesteia în sistemul naţional privind factura electronică RO e-Factura."
— OUG 120/2021, art. 4 alin. (4)
:::

Legea descrie rezultatul final (semnătura MF aplicată), fără să detalieze etapa intermediară de așteptare. Pentru o factură emisă, transmisă cu succes către ANAF, dar pentru care ANAF nu a dat încă un verdict, starea de "așteptare" este cea uzuală, nu o excepție sau o problemă.

## Ce se greșește în practică

- Se caută facturile "în așteptare" printre cele primite de la furnizori, deși e vorba de propriile facturi emise, aflate în curs de validare la ANAF — fluxurile sunt separate.
- Se interpretează starea de așteptare ca fiind deja o problemă, deși ea reprezintă doar intervalul normal dintre încărcarea facturii și verdictul definitiv al ANAF.
- Se așteaptă o actualizare instantanee a stadiului, ignorând faptul că verificarea la ANAF se face periodic, nu în timp real, continuu.

## Ce face iConta.eu

iConta.eu urmărește automat toate facturile emise, deja încărcate în SPV, care nu au primit încă un verdict terminal de la ANAF, și le interoghează periodic, la fiecare 30 de minute. Cât timp răspunsul ANAF rămâne "în prelucrare", factura este menținută în această stare de așteptare. Dacă starea de așteptare depășește un prag intern conservator de 2 zile, aplicația o marchează distinct ("investigație"), ca semnal că merită verificare manuală directă în SPV — factura nu este niciodată abandonată tăcut din urmărire.

Menționăm onest o limitare: nu am confirmat existența unui ecran dedicat, separat, care să afișeze exclusiv o listă filtrată cu facturile emise aflate în așteptare la nivelul firmei — starea de așteptare există și e urmărită în evidența internă a fiecărei trimiteri, dar o funcție de portofoliu dedicată listării lor separate nu a fost verificată ca disponibilă.

[iConta.eu](/)
