---
title: Indemnizația de boală - cum se calculează baza de calcul?
description: Baza de calcul a indemnizației de concediu medical este media veniturilor brute din ultimele 6 luni, plafonată lunar la 12 salarii minime, la care se aplică procentul legal în funcție de codul de boală și durata episodului.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Indemnizația de boală - cum se calculează baza de calcul?

Cuantumul unui concediu medical nu pornește direct din salariul brut al lunii curente, ci dintr-o medie a veniturilor din ultimele 6 luni, plafonată. Peste această bază de calcul se aplică apoi un procent care depinde de codul de boală înscris pe certificat și, pentru concediul obișnuit (cod 01), de durata episodului.

## Temeiul legal

::: ghid-temei
**OUG 158/2005, Articolul 10, alin.(1):** *"...baza de calcul al indemnizațiilor... se determină ca medie a veniturilor brute lunare din ultimele 6 luni din cele 12 luni din care se constituie stagiul de asigurare, până la limita a 12 salarii minime brute pe țară LUNAR, pe baza cărora se calculează contribuția asiguratorie pentru muncă."*

**OUG 158/2005, Articolul 10, alin.(8)-(9):** *"Din duratele de acordare a concediilor medicale, exprimate în zile calendaristice, se plătesc zilele lucrătoare"* + zilele de sărbătoare nelucrătoare excluse.

**OUG 158/2005, Articolul 17, alin.(1), forma în vigoare de la 01.08.2025 (Legea 141/2025, art.IX):** *"a) prin aplicarea procentului de 55% asupra bazei de calcul... pentru certificatele... eliberate pentru o perioadă de până la 7 zile...; b)... 65%... între 8 și 14 zile...; c)... 75%... pentru o perioadă de PESTE 15 zile de incapacitate temporară de muncă."*

**Legea 141/2025, Articolul X:** *"Prevederile art. VIII și IX intră în vigoare la data de 1 august 2025."*

**OUG 158/2005 (formă pre-Legea 141/2025), Articolul 17 alin.(1):** *"se determină prin aplicarea procentului de 75% asupra bazei de calcul stabilite conform art. 10"*
:::

## Cum se calculează practic baza de calcul

Baza de calcul (numită și Mzbci, media zilnică a bazei de calcul a indemnizației) se obține astfel:

1. Se adună veniturile brute lunare din ultimele 6 luni anterioare lunii îmbolnăvirii, din cele 12 luni de stagiu de asigurare.
2. Fiecare venit lunar este plafonat individual la 12 salarii minime brute **ale lunii respective** — plafonarea se face lună cu lună, înainte de a face media, nu pe suma totală.
3. Suma astfel plafonată se împarte la numărul total de zile lucrătoare din cele 6 luni.
4. Rezultatul (Mzbci) se înmulțește cu procentul legal aplicabil codului de boală și cu numărul de zile din certificat (eventual diminuat, vezi ghidul despre cine plătește primele zile de concediu medical).

Pentru concediul medical obișnuit (cod 01), procentul nu mai este uniform din 01.08.2025: crește progresiv cu durata episodului — 55% până la 7 zile, 65% între 8 și 14 zile, 75% peste 15 zile. Înainte de 01.08.2025, procentul era unic, 75%, indiferent de durată.

::: ghid-exemplu
Un salariat are un episod de boală de 10 zile (cod 01), eliberat după 01.08.2025. Mzbci calculată din ultimele 6 luni este 200 lei/zi. Se aplică procentul pentru tranșa 8-14 zile, adică 65%: indemnizație brută = 200 × 65% × 10 zile = 1.300 lei, înainte de eventuale diminuări sau rotunjiri.
:::

O situație de graniță semnalată explicit: textul legal acoperă până la 14 zile la tranșa de 65% și "peste 15 zile" la tranșa de 75%, dar nu menționează literal exact ziua 15. Este un gol de redactare confirmat la sursă. Practica aplicată favorizează asiguratul, tratând ziua 15 ca fiind în tranșa de 75% — o interpretare documentată, nu o eroare ascunsă.

## Ce se greșește în practică

- Se calculează baza de calcul din salariul brut al lunii curente, în loc de media ultimelor 6 luni.
- Se plafonează suma totală a celor 6 luni la 12 salarii minime, în loc să se plafoneze fiecare lună individual, cu salariul minim valabil în luna respectivă.
- Se aplică procentul unic de 75% și pentru certificatele eliberate după 01.08.2025, ignorând scara progresivă 55/65/75%.
- Se ia în calcul procentul valabil la data certificatului curent, în loc de procentul valabil la data certificatului INIȚIAL al episodului, atunci când boala continuă pe mai multe certificate.
- Se împarte suma plafonată la numărul de zile calendaristice, nu la zilele lucrătoare din cele 6 luni.

## Ce face iConta.eu

Motorul de calcul aplică formula `Ci = Mzbci × procent% × (NZLCM − diminuare)`. Media zilnică (Mzbci) se calculează prin plafonarea FIECĂRUI venit lunar la 12 salarii minime ale lunii respective ÎNAINTE de mediere, apoi împărțirea sumei plafonate la totalul zilelor lucrătoare din acele 6 luni. Procentul aplicabil este determinat de funcția care alege, pentru codul 01, între forma veche (uniformă, 75%, până la 31.07.2025) și forma progresivă (55/65/75%, de la 01.08.2025), pe baza datei certificatului inițial al episodului, nu a certificatului curent. Pentru cazul-limită al zilei 15, aplicația tratează ziua ca fiind în tranșa de 75%, decizie documentată intern ca fiind favorabilă asiguratului, întrucât textul legal nu acoperă literal acest caz.

[iConta.eu](/)
