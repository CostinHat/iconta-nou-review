---
title: "Cum se declară în D112 un salariat care pleacă în cursul lunii?"
description: "Cum se proratează plafonul minim de CAS/CASS pentru un contract activ doar o parte din lună, potrivit Normelor de aplicare a Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se declară în D112 un salariat care pleacă în cursul lunii?

Când contractul individual de muncă încetează în cursul lunii, plafonul minim la care se raportează contribuțiile sociale (art. 146 alin. (5^1) Cod fiscal) nu se aplică la nivelul întregului salariu minim pe economie, ci proporțional cu zilele în care contractul a fost activ.

## Temeiul legal

::: ghid-temei
„În sensul aplicării prevederilor art. 146 alin. (5^1) din Codul fiscal, prin perioada în care contractul individual de muncă este activ se înțelege perioada în care contractul individual de muncă nu este suspendat potrivit Legii nr. 53/2003, republicată, cu modificările și completările ulterioare. În cazul în care, în cursul lunii, contractul individual de muncă este activ pentru o fracțiune din lună, nivelul salariului minim brut pe țară aferent zilelor lucrate din lună se stabilește după cum urmează: [...]"
— HG 1/2016 (Normele de aplicare a Codului fiscal), Titlul V, Capitolul II, Secțiunea a 3-a, pct. 6 alin. (3) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

Din text rezultă principiul aplicabil oricărui salariat care pleacă (sau este angajat) în cursul lunii:

- **Contractul activ** înseamnă perioada în care nu e suspendat potrivit Codului muncii — deci se numără doar zilele lucrătoare din intervalul cât contractul a fost efectiv activ, nu toate zilele calendaristice ale lunii.
- **Nivelul salariului minim de referință** pentru acea lună se calculează proporțional cu zilele lucrate din lună, nu la valoarea întreagă a salariului minim brut pe țară.
- În D112, angajatul apare cu perioada corectă de activitate în lună (data angajării și/sau data încetării), iar baza de calcul CAS/CASS, respectiv verificarea încadrării la minimul pe economie, trebuie raportată la această fracțiune de lună, nu la luna întreagă.

## Ce se greșește în practică

- Se compară salariul brut efectiv (pentru zilele lucrate) cu salariul minim pe economie al lunii întregi, deși pentru o fracțiune de lună termenul de comparație corect e proratat.
- Se omite din D112 data încetării contractului, ceea ce face ca sistemul angajatorului să calculeze automat contribuțiile ca pentru o lună completă.
- Se confundă suspendarea contractului (de exemplu concediu fără plată) cu încetarea lui — doar perioada de contract activ, nesuspendat, intră în calculul zilelor de referință potrivit pct. 6 alin. (3).

## Ce face iConta.eu

La data acestui ghid, iConta.eu **calculează automat, la nivel de zi, dacă un contract a fost activ și la ce nivel de salariu**, plecând de la istoricul salarial și de la data angajării/încetării fiecărui salariat, pentru a determina corect numărul de zile din lună în care salariul e la nivelul minim pe economie — bază folosită de aplicație pentru proratarea unor facilități legate de acest prag. Datele de angajare și încetare introduse de contabil în fișa salariatului sunt cele care alimentează, prin acest calcul, generarea corectă a stat de plată și a declarației D112 pentru luna în care contractul se încheie.

[iConta.eu](/)
