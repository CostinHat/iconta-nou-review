---
title: "Cum verific statusul unei facturi după indexul de încărcare?"
description: Ce este indexul de încărcare primit de la ANAF la trimiterea unei facturi electronice și cum se folosește pentru a interoga stadiul acesteia.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum verific statusul unei facturi după indexul de încărcare?

Când o factură este încărcată cu succes în SPV, ANAF returnează un identificator unic — indexul de încărcare. Acest identificator este exact ceea ce se folosește, ulterior, pentru a interoga la ANAF stadiul acelei trimiteri.

## Temeiul legal

::: ghid-temei
"În situaţia în care factura electronică transmisă respectă structura prevăzută la alin. (1), se aplică semnătura electronică a Ministerului Finanţelor şi se comunică de îndată destinatarului. Aplicarea semnăturii electronice a Ministerului Finanţelor atestă primirea acesteia în sistemul naţional privind factura electronică RO e-Factura."
— OUG 120/2021, art. 4 alin. (4)
:::

Legea nu numește explicit termenul "index de încărcare" — acesta este identificatorul tehnic pe care ANAF îl returnează la primirea reușită a unei facturi în sistem, folosit apoi pentru a afla, la interogare, dacă s-a aplicat sau nu semnătura electronică a Ministerului Finanțelor (adică dacă factura a fost acceptată) sau dacă a fost respinsă.

Indexul de încărcare este disponibil doar după ce încărcarea facturii în SPV a reușit — o factură care nu a ajuns deloc la ANAF (eroare de upload) nu are un index de încărcare de folosit pentru interogare.

## Ce se greșește în practică

- Se încearcă interogarea stadiului unei facturi înainte ca aceasta să fi fost efectiv încărcată cu succes în SPV — fără index de încărcare valid, nu există ce interoga.
- Se confundă indexul de încărcare (primit la upload) cu identificatorul de descărcare a recipisei — cel din urmă este un identificator diferit, primit abia la momentul verdictului terminal (favorabil sau nefavorabil), nu la încărcare.
- Se așteaptă un răspuns instant la interogarea stadiului după index — verificarea reală a stadiului la ANAF se face periodic, nu la cerere imediată, continuă.

## Ce face iConta.eu

La fiecare încărcare reușită a unei facturi în SPV, iConta.eu reține indexul de încărcare primit de la ANAF și îl folosește ca reper pentru interogările ulterioare de stadiu. La fiecare rulare automată, la 30 de minute, aplicația interoghează ANAF pentru stadiul fiecărei facturi care are un index de încărcare valid și se află încă în așteptarea unui verdict — și actualizează starea internă a facturii pe baza răspunsului primit.

Menționăm onest o limitare: interogarea folosind indexul de încărcare se face automat, în cadrul rulărilor programate ale aplicației, nu ca o verificare punctuală, la cerere, declanșată manual de utilizator din interfață — la momentul acestei verificări, o funcție dedicată de interogare manuală, imediată, pe baza indexului nu a fost confirmată ca disponibilă.

[iConta.eu](/)
