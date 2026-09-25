---
title: "Cum se calculează concediul medical în 2026?"
description: "Pașii calculului de concediu medical în 2026: baza pe 6 luni, procentul pe cod, diminuarea de 1 zi introdusă de OUG 91/2025 și ce parte a calculului o face iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează concediul medical în 2026?

Anul 2026 aduce, pe lângă formula de bază din OUG 158/2005, o regulă suplimentară care schimbă efectiv suma primită: pentru certificatele eliberate între 1 februarie 2026 și 31 decembrie 2027, indemnizația se calculează **cu o zi mai puțin**. Calculul complet trece, deci, prin trei pași: baza de calcul, procentul pe cod, apoi diminuarea de o zi, dacă se aplică.

## Temeiul legal

::: ghid-temei
„Pentru persoanele prevăzute la art. 1 alin. (1) lit. A și B, baza de calcul al indemnizațiilor prevăzute la art. 2 se determină ca medie a veniturilor brute lunare din ultimele 6 luni din cele 12 luni din care se constituie stagiul de asigurare, până la limita a 12 salarii minime brute pe țară lunar [...]."

„Pentru certificatele de concediu medical eliberate în perioada 1 februarie 2026-31 decembrie 2027, indemnizațiile de asigurări sociale de sănătate prevăzute prin [OUG 158/2005] [...] se calculează și se plătesc prin diminuarea cu o zi și se suportă după cum urmează: a) de către angajator, din a 2-a zi până inclusiv în a 6-a zi de incapacitate temporară de muncă [...]; b) din bugetul [FNUASS], începând cu: (i) ziua următoare celor suportate de angajator [...]."
— OUG 158/2005, art. 10 alin. (1) (sursă: anaf_surse/oug_158_2005_consolidat.txt); OUG 91/2025, art. II alin. (1) (sursă: anaf_surse/oug_91_2025.txt)
:::

Pașii calculului, în ordine:

1. **Baza de calcul** — media veniturilor brute lunare din ultimele 6 luni, plafonată la 12 salarii minime brute pe lună.
2. **Procentul**, ales după codul indemnizației de pe certificat (55/65/75% progresiv pentru boală obișnuită, alte procente fixe pentru maternitate, îngrijire copil, carantină etc.) și, pentru boala obișnuită, după durata certificatului.
3. **Diminuarea de 1 zi**, activă pentru certificatele eliberate 1 februarie 2026 – 31 decembrie 2027: prima zi din episod nu se mai plătește, iar zilele suportate de angajator se mută cu o zi (a 2-a până în a 6-a zi, nu 1–5 ca în regula clasică). Legea prevede și excepții de la această diminuare (spitalizare, programe naționale de sănătate, anumite coduri de indemnizație), introduse ulterior prin Legea 64/2026.

## Ce se greșește în practică

- Se calculează indemnizația după formula veche (fără diminuarea de o zi), pentru certificate eliberate deja în fereastra 1 februarie 2026 – 31 decembrie 2027.
- Se aplică diminuarea de o zi și la certificate care intră în categoriile exceptate prin lege (spitalizare, anumite coduri de indemnizație).
- Se omite plafonarea bazei de calcul la 12 salarii minime brute pe lună, la salariații cu venituri peste acest nivel.

## Ce face iConta.eu

Motorul de calcul (`core/salarizare.py`, funcția `calcul_cm`) e dispecerizat pe data certificatului și aplică automat regula corectă pentru 2026: baza pe 6 luni, procentul pe cod și, pentru certificatele din fereastra 1 februarie 2026 – 31 decembrie 2027, diminuarea de o zi, cu excepțiile ei. Nu există un ecran separat „calculator" — calculul rulează în spatele ecranului de introducere a certificatelor de concediu medical din fișa salariatului, unde contabilul completează certificatul și primește direct rezultatul.

O limitare reală, verificată în cod: plafonarea bazei de calcul la 12 salarii minime brute pe lună (art. 10 alin. (1)), deși motorul o suportă tehnic, nu se aplică în practică astăzi, pentru că niciun ecran din aplicație nu trimite veniturile defalcate pe fiecare din cele 6 luni — se introduce doar suma agregată. La salariați cu venituri peste plafon, indemnizația calculată poate ieși mai mare decât permite legea.

[iConta.eu](/)
