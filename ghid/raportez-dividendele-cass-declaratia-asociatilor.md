---
title: "Cum raportez dividendele pentru CASS în declarația asociaților"
description: "Cum se încadrează dividendele încasate de un asociat persoană fizică în plafoanele CASS (6/12/24 salarii minime brute) și cum se raportează prin Declarația unică."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum raportez dividendele pentru CASS în declarația asociaților

Dividendele încasate de o persoană fizică intră la categoria „venituri din investiții" pentru CASS, alături de dobânzi și câștiguri din instrumente financiare. Ele nu se impozitează separat cu CASS proporțional (ca la salarii), ci printr-un sistem de **plafoane fixe** — 6, 12 sau 24 de salarii minime brute pe țară — în funcție de nivelul cumulat al veniturilor de acest tip din anul respectiv.

## Temeiul legal

::: ghid-temei
„Baza anuală de calcul al contribuției de asigurări sociale de sănătate în cazul persoanelor care realizează venituri din cele prevăzute la art. 155 alin. (1) lit. c)-h) o reprezintă: a) nivelul a 6 salarii minime brute pe țară, în cazul veniturilor realizate cuprinse între 6 salarii minime brute pe țară inclusiv și 12 salarii minime brute pe țară; b) nivelul de 12 salarii minime brute pe țară, în cazul veniturilor realizate cuprinse între 12 salarii minime brute pe țară inclusiv și 24 de salarii minime brute pe țară; c) nivelul de 24 de salarii minime brute pe țară, în cazul veniturilor realizate cel puțin egale cu 24 de salarii minime brute pe țară."
— Legea 227/2015, art. 170 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul de raportare, pas cu pas:

- Veniturile din investiții definite la art. 91 (dividende, dobânzi, câștiguri din titluri de valoare, câștiguri din aur de investiții, venituri din lichidarea unei persoane juridice) se **cumulează** pe an calendaristic — plafonul nu se verifică separat pe fiecare sursă.
- Dacă suma cumulată e sub 6 salarii minime brute pe țară, nu se datorează CASS pe aceste venituri.
- Dacă suma e cel puțin 6 salarii minime, baza de calcul CASS nu e venitul efectiv, ci **plafonul în care se încadrează** (6, 12 sau 24 de salarii minime) — deci CASS se plătește la un nivel fix, indiferent cât de mult depășește venitul real acel prag, atât timp cât rămâne sub pragul următor.
- Raportarea se face prin Declarația unică (D212), la termenul legal de depunere prevăzut la art. 122 alin. (3) Cod fiscal — nu există o declarație separată doar pentru dividende; ele se agregă cu celelalte venituri din investiții în același capitol al D212.

## Ce se greșește în practică

- Se calculează CASS proporțional cu dividendul încasat (ex. 10% din dividend), ca la o reținere la sursă — de fapt CASS se aplică la baza plafonată (6/12/24 salarii minime), nu la venitul efectiv.
- Se ignoră obligația de cumulare cu alte venituri din investiții (dobânzi bancare, câștiguri din tranzacționare) atunci când se verifică dacă s-a atins pragul de 6 salarii minime.
- Se confundă impozitul pe dividende (16%, reținut de firmă prin D205) cu CASS-ul (datorat separat de asociat, prin D212, doar peste plafon) — sunt două obligații distincte, cu baze și mecanisme diferite.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu calculează automat plafonul CASS** al unui asociat persoană fizică: aplicația nu are un registru al persoanelor fizice și nici vizibilitate asupra veniturilor din investiții realizate de acesta din alte surse (alte firme, conturi bancare, brokeri). Generatorul de D212 emite formularul pe baza valorilor introduse manual — venituri, baze de calcul, CASS — fără să recalculeze cotele sau plafoanele; asociatul (sau contabilul lui) trebuie să facă însumarea și încadrarea pe cele trei praguri înainte de completare. Ceea ce iConta.eu oferă cert este dividendul brut plătit, calculat corect prin D205, ca punct de plecare pentru acest calcul.

[iConta.eu](/)
