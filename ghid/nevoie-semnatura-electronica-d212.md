---
title: "Am nevoie de semnătură electronică pentru D212?"
description: "Când este obligatoriu certificatul digital calificat pentru depunerea Declarației unice (D212) și pentru cine este opțională o altă metodă de identificare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Am nevoie de semnătură electronică pentru D212?

Da, dacă depui D212 ca persoană fizică ce desfășoară o activitate economică independentă (PFA, întreprindere individuală, întreprindere familială) sau exerciți o profesie liberală. Legea impune, pentru această categorie, identificarea în relația cu organul fiscal **numai** cu certificat digital calificat — nu există altă opțiune, precum utilizator/parolă.

## Temeiul legal

::: ghid-temei
„(1) Contribuabilul/Plătitorul care depune cereri, înscrisuri sau documente la organul fiscal, prin mijloace electronice de transmitere la distanță, se identifică în relația cu organul fiscal astfel: a) persoanele juridice, asocierile și alte entități fără personalitate juridică, precum și persoanele fizice care desfășoară activități economice în mod independent ori exercită profesii libere se identifică numai cu certificate calificate; b) persoanele fizice, altele decât cele prevăzute la lit. a), se identifică prin intermediul furnizorilor de servicii publice de autentificare electronică autorizați potrivit legii sau prin diverse dispozitive, cum ar fi certificat calificat, credențiale de tip utilizator/parolă însoțite de liste de coduri de autentificare de unică folosință, telefon mobil, digipass ori alte dispozitive [...]."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 80 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă de aici:

- Legea distinge două categorii de persoane fizice: (a) cele care desfășoară activități economice independente sau exercită profesii liberale — obligate la certificat calificat; și (b) toate celelalte persoane fizice — care pot folosi și alte metode (utilizator/parolă cu coduri de autentificare de unică folosință, telefon mobil, digipass etc.).
- Un salariat care depune, de exemplu, o declarație privind veniturile din chirii ocazionale poate folosi metodele mai simple de la lit. b). O PFA care depune D212 pentru veniturile din activitatea proprie se încadrează însă la lit. a) și trebuie să folosească certificat calificat.
- Certificatul digital calificat se obține contra cost de la un furnizor de servicii de certificare acreditat și trebuie instalat/asociat contului de SPV al contribuabilului înainte de depunerea declarației.

## Ce se greșește în practică

- Se încearcă autentificarea în SPV, pentru depunerea D212 ca PFA, cu utilizator/parolă (metodă validă doar pentru persoanele fizice fără activitate independentă), ceea ce blochează sau invalidează transmiterea.
- Se amână achiziționarea certificatului digital calificat până aproape de termenul legal de depunere (25 mai), riscând să nu mai poată fi obținut și instalat la timp.
- Se confundă certificatul calificat al PFA cu cel al firmei (SRL) la care aceeași persoană este și administrator — sunt, de regulă, certificate/înrolări diferite, în funcție de calitatea în care se depune declarația.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează fișierul XML al Declarației unice (D212) pe baza datelor introduse de contabil (`core/d212.py`), dar nu gestionează certificate digitale calificate și nu efectuează el însuși autentificarea în SPV. Obținerea certificatului calificat și autentificarea/transmiterea în Spațiul Privat Virtual rămân proceduri realizate direct de contribuabil sau de contabil, în afara aplicației.

[iConta.eu](/)
