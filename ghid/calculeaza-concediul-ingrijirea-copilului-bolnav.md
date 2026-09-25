---
title: "Cum se calculează concediul pentru îngrijirea copilului bolnav?"
description: "Vârsta copilului, cuantumul indemnizației și cine o poate solicita, potrivit OUG nr. 158/2005 privind concediile și indemnizațiile de asigurări sociale de sănătate."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se calculează concediul pentru îngrijirea copilului bolnav?

Concediul pentru îngrijirea copilului bolnav e un drept separat de concediul medical propriu al asiguratului, cu vârstă-limită proprie și cuantum stabilit distinct, în funcție de baza de calcul a asiguratului.

## Temeiul legal

::: ghid-temei
„Asigurații au dreptul la concediu și indemnizație pentru îngrijirea copilului bolnav în vârstă de până la 12 ani, iar în cazul copilului cu handicap, pentru afecțiunile intercurente, până la împlinirea vârstei de 18 ani."
— OUG nr. 158/2005, art. 26 alin. (1) (sursă: anaf_surse/oug_158_2005_consolidat.txt)

„Beneficiază de indemnizația pentru îngrijirea copilului bolnav, opțional, unul dintre părinți, dacă solicitantul îndeplinește condițiile de stagiu de asigurare prevăzute la art. 7."
— OUG nr. 158/2005, art. 27 alin. (1) (sursă: anaf_surse/oug_158_2005_consolidat.txt)

„Cuantumul brut lunar al indemnizațiilor prevăzute la art. 26 alin. (1) și (1^1) este de 85% din baza de calcul stabilită conform art. 10."
— OUG nr. 158/2005, art. 30 alin. (1) (sursă: anaf_surse/oug_158_2005_consolidat.txt)
:::

Ce rezultă din cele trei texte, combinate:

- **Vârsta copilului**: dreptul se acordă până la 12 ani, pentru orice afecțiune; se extinde până la 18 ani doar pentru copilul cu handicap, pentru afecțiuni intercurente (adică diferite de handicapul de bază), respectiv până la 18 ani și pentru copilul cu afecțiuni grave, conform completărilor ulterioare ale art. 26.
- **Cine solicită**: dreptul e opțional pentru **unul dintre părinți** — nu se cumulează, iar condiția de bază e îndeplinirea stagiului de asigurare cerut de art. 7 din aceeași ordonanță.
- **Cuantumul**: indemnizația e de **85% din baza de calcul** stabilită conform art. 10 (media veniturilor din ultimele luni, potrivit regulilor generale ale ordonanței) — nu 100%, ca la unele tipuri de concediu medical, și nu o sumă fixă.
- Indemnizația se suportă integral din bugetul Fondului național unic de asigurări sociale de sănătate, nu din bugetul angajatorului — spre deosebire de primele zile ale unor tipuri de concediu medical obișnuit, plătite de angajator.

## Ce se greșește în practică

- Se calculează indemnizația la 100% din baza de calcul, confundând-o cu alte tipuri de concediu (de exemplu cel pentru afecțiuni oncologice sau pentru carantină, care au procente diferite) — pentru îngrijirea copilului bolnav „standard", procentul e 85%.
- Se acordă concediul pentru un copil peste 12 ani fără verificarea prealabilă a încadrării în excepțiile legale (handicap cu afecțiune intercurentă, respectiv afecțiune gravă din lista stabilită de Ministerul Sănătății) — fără această încadrare, dreptul încetează la împlinirea a 12 ani.
- Se solicită concediul simultan de ambii părinți pentru aceeași perioadă, deși legea îl acordă opțional unui singur părinte.

## Ce face iConta.eu

Modulul de salarizare din iConta.eu urmărește episoadele de concediu medical ale angajaților, inclusiv cele legate de îngrijirea unui copil (evidența CNP-ului persoanei îngrijite, în `core/salarizare.py`), și calculează indemnizația pe baza cuantumului procentual corespunzător tipului de concediu, aplicat asupra bazei de calcul din certificatul medical introdus. Încadrarea corectă a vârstei copilului în excepțiile legale (handicap, afecțiune gravă) rămâne o verificare a contabilului, pe baza certificatului medical și a documentelor justificative primite de la angajat.

[iConta.eu](/)
