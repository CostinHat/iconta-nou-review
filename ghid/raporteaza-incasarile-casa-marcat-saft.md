---
title: "Cum se raportează încasările prin casa de marcat în SAF-T?"
description: "Jurnalele auxiliare de operațiuni de casă, prevăzute de normele contabile, stau la baza secțiunii de plăți din SAF-T (D406), inclusiv pentru încasările în numerar."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se raportează încasările prin casa de marcat în SAF-T?

SAF-T nu are o secțiune separată, dedicată strict aparatelor de marcat electronice — încasările prin casa de marcat ajung în raportare prin secțiunea de plăți, ca parte a operațiunilor de casă, așa cum sunt ele înregistrate în contabilitate.

## Temeiul legal

::: ghid-temei
„Entitățile pot utiliza jurnale auxiliare pe feluri de operațiuni, cum sunt: operațiuni de casă și bancă, operațiuni privind decontările cu furnizorii, situația încasării-achitării facturilor, operațiuni privind salariile și contribuția pentru asigurări sociale, protecția socială a șomerilor și asigurările de sănătate, alte operațiuni."
— OMFP nr. 2634/2015, Anexa 1 pct. 52 (sursă: anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt)
:::

Coroborat cu structura SAF-T (secțiunea „Payments" din fișierul D406, care conține „detalii despre plăţi, precum perioada, ID-ul tranzacţiei, data tranzacţiei, descriere, liniile de plăţi"), rezultă practic:

- Încasările prin numerar — inclusiv cele realizate prin casa de marcat, dacă au fost înregistrate contabil ca operațiune de casă — se raportează în SAF-T ca parte a jurnalului de operațiuni de casă și bancă, cu metoda de plată corespunzătoare (numerar).
- Norma contabilă (OMFP 2634/2015) definește felurile de jurnale auxiliare la nivel de principiu — SAF-T le preia și le structurează în format XML, dar sursa datelor rămâne evidența contabilă a jurnalului de casă, nu direct raportul Z al aparatului de marcat.
- Nu a fost identificat, în sursele ANAF verificate, un text care să impună o legătură automată, obligatorie, între datele de la aparatul de marcat electronic fiscal (reglementat de OUG 28/1999) și secțiunea SAF-T — legătura se face indirect, prin faptul că încasările respective sunt, la rândul lor, înregistrate contabil în jurnalul de casă.

## Ce se greșește în practică

- Se presupune că raportul Z zilnic al casei de marcat trebuie încărcat separat, ca fișier distinct, în D406 — SAF-T nu are o astfel de secțiune specifică pentru rapoartele AMEF; datele relevante sunt cele deja înregistrate contabil.
- Se omite înregistrarea zilnică a încasărilor din numerar în jurnalul de casă, ceea ce lasă un gol în raportarea SAF-T, deși vânzările efective au avut loc.
- Se confundă obligația de utilizare a aparatelor de marcat (OUG 28/1999) cu obligația de raportare SAF-T — sunt două obligații separate, care se întâlnesc doar în măsura în care încasările respective ajung, prin înregistrare contabilă, în jurnalul de casă raportat prin D406.

## Ce face iConta.eu

iConta.eu mapează explicit sursele de numerar din contabilitate — inclusiv cele descrise ca „numerar", „casa" sau „chitanță" — pe codul de metodă de plată corespunzător din nomenclatorul SAF-T, în generatorul `core/d406.py`. Jurnalul de casă este tratat ca jurnal auxiliar distinct (identificat „CASA" în structura internă), conform categoriilor din OMFP 2634/2015. Aplicația **nu importă însă automat datele brute din aparatele de marcat electronice fiscale** direct în D406 — ea are un modul separat de import din casa de marcat (`core/amef_import.py`), iar SAF-T se generează din ceea ce a fost efectiv înregistrat în evidența contabilă, nu direct din rapoartele Z ale AMEF.

[iConta.eu](/)
