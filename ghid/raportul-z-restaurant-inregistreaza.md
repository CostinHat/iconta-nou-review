---
title: "Raportul Z la restaurant: cum se înregistrează"
description: Un singur flux, două căi — import fișier AMEF (notă ciornă) sau introducere manuală (notă validată direct). Unicitatea raportului se ține pe NUI casă de marcat + număr, nu pe dată.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Raportul Z la restaurant: cum se înregistrează

Pentru un restaurant, Raportul Z e documentul zilnic care intră în contabilitate în locul unei facturi — vezi pe scurt cele două căi disponibile și regula care ține evidența fără duplicate.

## Temeiul legal

::: ghid-temei
„conțin datele aferente fiecărei zile fiscale încheiate" — OPANAF 146/2018 (norma metodologică pentru aplicarea OUG 28/1999), descrierea rapoartelor de la secțiunile II.1-II.7 ale anexei 2
:::

## Cele două căi

**Import de fișier AMEF** — se încarcă direct p7b-ul sau XML-ul generat de casa de marcat. Aplicația citește totalurile pe fiecare cotă de TVA apărută efectiv în fișier și plățile pe tip (card, numerar, tichete etc.). Nota rezultată e **ciornă**, verificabilă înainte să intre definitiv în evidență.

**Introducere manuală** — Data, NUI-ul casei de marcat, numărul raportului, totalurile pe 11% (mâncare) și 21% (alcool, sucuri), numerar și card. TVA se calculează automat prin sută mărită. Nota rezultată e generată **direct ca validată**, fără pasul intermediar de ciornă.

## Cum se evită dublarea

Cheia care ține unicitatea raportului e combinația **NUI casă de marcat + număr raport Z**, nu data calendaristică — număr de raport care e oricum secvențial pe fiecare casă de marcat, deci nu se repetă. Un al doilea import sau o a doua introducere manuală cu aceeași combinație e refuzată, cu mesaj care indică nota deja existentă — nu se creează silențios o a doua notă pentru același Z.

## Ce se greșește în practică

Reintroducerea manuală a unui Z deja importat prin fișier AMEF, pentru „siguranță" — mecanismul de unicitate o va respinge, dar mesajul de eroare trebuie citit, nu ocolit prin modificarea numărului de raport doar ca să treacă. A doua greșeală: presupunerea că data e cea care garantează unicitatea — de fapt e strict combinația NUI+număr.

## Ce face iConta.eu

Unicitatea e impusă atât la nivel de verificare rapidă în aplicație, cât și printr-un index unic în baza de date — dubla protecție acoperă și situația în care două cereri ajung aproape simultan. Politica aplicației la un duplicat detectat e să nu șteargă și să nu aleagă automat nota corectă — raportează refuzul și cere verificare manuală.

[iConta.eu](/)
