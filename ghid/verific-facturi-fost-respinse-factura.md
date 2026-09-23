---
title: "Cum verific ce facturi au fost respinse de e-Factura?"
description: Ce înseamnă starea de respingere pentru facturile emise de firma dumneavoastră și transmise prin RO e-Factura, și ce e disponibil momentan pentru identificarea lor.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum verific ce facturi au fost respinse de e-Factura?

Această întrebare privește facturile pe care firma dumneavoastră **le-a emis și le-a trimis** către ANAF prin RO e-Factura — nu facturile primite de la furnizori, care urmează un flux separat, cu propriile stări. Pentru facturile emise, respingerea este un verdict terminal, primit de la ANAF la interogarea stadiului transmiterii.

## Temeiul legal

::: ghid-temei
"În situaţia în care factura electronică transmisă nu respectă structura prevăzută la alin. (1), emitentul primeşte mesaj cu erorile identificate. După corectarea erorilor identificate, factura electronică se transmite în cadrul aceluiaşi sistem naţional privind factura electronică RO e-Factura."
— OUG 120/2021, art. 4 alin. (5)
:::

Legea confirmă mecanismul: respingerea vine cu un mesaj de eroare, iar corectarea presupune o transmitere nouă. Nu descrie însă un mod standard de a "lista" facturile respinse la nivelul unei firme — asta e o funcționalitate a aplicației folosite pentru gestiunea facturilor, nu o cerință legală.

## Ce se greșește în practică

- Se caută facturile respinse din fluxul facturilor primite de la furnizori, deși întrebarea privește propriile facturi emise — sunt două fluxuri distincte, cu tabele și logici diferite în orice sistem care le gestionează.
- Se presupune că respingerea e vizibilă instant, imediat după transmitere — de fapt, verdictul de respingere e primit abia la interogarea stadiului, care se face periodic, nu în timp real.
- Se ignoră faptul că o factură cu eroare de upload (netransmisă efectiv la ANAF) e o situație diferită de o factură transmisă și ulterior respinsă de ANAF — prima nu a ajuns la un verdict, a doua a primit deja unul.

## Ce face iConta.eu

iConta.eu urmărește automat stadiul fiecărei facturi emise, transmise deja către ANAF, prin interogare periodică la fiecare 30 de minute. Când ANAF răspunde cu un verdict nefavorabil, factura respectivă este marcată ca respinsă în evidența internă, iar mesajul de eroare primit de la ANAF este salvat exact așa cum a fost returnat.

Trebuie spus onest: la acest moment nu am confirmat existența unui ecran dedicat, separat, care să afișeze o listă filtrată exclusiv cu facturile emise respinse la nivelul firmei — marcajul de respingere există în evidența internă a fiecărei trimiteri, dar o funcție de portofoliu dedicată listării lor separate nu a fost verificată ca disponibilă. Dacă aveți nevoie de o astfel de listare, recomandăm verificarea directă, punctual, a facturilor cu verdict nefavorabil.

[iConta.eu](/)
