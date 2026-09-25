---
title: "Concediul medical 2026: cum se calculează indemnizația"
description: "Formula legală a indemnizației de concediu medical în 2026 — baza pe 6 luni, plafonul de 12 salarii minime și procentul progresiv — și ce calculează efectiv motorul din iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Concediul medical 2026: cum se calculează indemnizația

Indemnizația de concediu medical nu e un procent fix aplicat la salariu, cum se crede adesea. E rezultatul a doi pași distincți, stabiliți prin OUG 158/2005: mai întâi se calculează o **bază de calcul**, pornind de la veniturile din ultimele 6 luni, apoi peste această bază se aplică un **procent** care depinde de codul indemnizației și, pentru boala obișnuită, de durata certificatului.

## Temeiul legal

::: ghid-temei
„Pentru persoanele prevăzute la art. 1 alin. (1) lit. A și B, baza de calcul al indemnizațiilor prevăzute la art. 2 se determină ca medie a veniturilor brute lunare din ultimele 6 luni din cele 12 luni din care se constituie stagiul de asigurare, până la limita a 12 salarii minime brute pe țară lunar, pe baza cărora se calculează contribuția asiguratorie pentru muncă."

„Cuantumul brut lunar al indemnizației pentru incapacitate temporară de muncă cauzată de boli obișnuite sau de accidente în afara muncii se determină raportat la fiecare episod de boală, după cum urmează: a) prin aplicarea procentului de 55% asupra bazei de calcul stabilite conform art. 10 pentru certificatele de concediu medical eliberate pentru o perioadă de până la 7 zile [...]; b) [...] 65% [...] între 8 și 14 zile [...]; c) [...] 75% [...] pentru [...] o perioadă de peste 15 zile [...]."
— OUG 158/2005, art. 10 alin. (1) și art. 17 alin. (1) (sursă: anaf_surse/oug_158_2005_consolidat.txt)
:::

Din text rezultă mecanica exactă a calculului:

- **Baza de calcul** = media veniturilor brute lunare din ultimele 6 luni din cele 12 în care s-a constituit stagiul de asigurare, **plafonată la 12 salarii minime brute pe țară pe lună** — indiferent cât de mare a fost venitul real, nu se ia în calcul nimic peste acest plafon lunar.
- **Procentul**, pentru boală obișnuită sau accident în afara muncii (codul 01), e progresiv, în funcție de durata certificatului: **55%** până la 7 zile, **65%** între 8 și 14 zile, **75%** pentru peste 15 zile — regulă valabilă de la 1 august 2025 (Legea 141/2025); certificatele mai vechi, pentru episoade începute înainte de această dată, rămân la vechiul procent unic de 75%.
- Alte coduri de indemnizație (maternitate, îngrijire copil, carantină etc.) au procente proprii, fixate de alte articole din aceeași ordonanță (85%, 100% etc.), nu formula progresivă de mai sus.

## Ce se greșește în practică

- Se aplică un procent unic de 75% la toate certificatele cod 01, indiferent de câte zile are certificatul — regulă valabilă doar pentru episoadele începute înainte de 1 august 2025.
- Se calculează media pe 6 luni din venitul brut real, fără să se verifice dacă vreo lună depășește plafonul de 12 salarii minime brute — la salariați cu venituri mari, omiterea plafonării umflă artificial indemnizația.
- Se confundă zilele calendaristice înscrise pe certificat cu zilele plătite efectiv — din durata calendaristică se plătesc doar zilele lucrătoare.

## Ce face iConta.eu

Motorul de calcul (`core/salarizare.py`, funcțiile `calcul_cm` și `procent_cm`) aplică exact procentele progresive de mai sus, dispecerizate pe data certificatului, și calculează media zilnică din baza pe 6 luni primită ca parametru. Acest motor nu are un ecran „calculator" de sine stătător — e folosit intern, prin ecranul de introducere a certificatelor de concediu medical al unui salariat (secțiunea Concedii din fișa salariatului), unde contabilul completează codul, perioada și **suma veniturilor din ultimele 6 luni, introdusă manual**, iar aplicația calculează automat baza, procentul și indemnizația. Există și un modul separat (`core/baza_cm.py`) care poate aduna automat veniturile pe 6 luni din statele de plată deja emise, dar el e conectat doar la un API intern, fără ecran propriu — ecranul folosit efectiv de contabil nu-l apelează.

O limitare reală, verificată în cod: deși motorul suportă tehnic plafonarea la 12 salarii minime din art. 10 alin. (1), niciun ecran din aplicație nu trimite astăzi veniturile defalcate pe fiecare din cele 6 luni (parametrul opțional care activează plafonarea) — formularul cere doar suma și zilele agregate pe 6 luni. În consecință, la un salariat cu venituri peste plafonul legal, indemnizația calculată azi de iConta.eu poate ieși mai mare decât permite legea, pentru că plafonarea lunară nu se aplică în practică.

[iConta.eu](/)
