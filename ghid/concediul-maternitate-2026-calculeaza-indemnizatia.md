---
title: "Concediul de maternitate 2026: cum se calculează indemnizația"
description: "Durata concediului de maternitate și formula de calcul a indemnizației, conform OUG 158/2005 privind concediile și indemnizațiile de asigurări sociale de sănătate."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Concediul de maternitate 2026: cum se calculează indemnizația

Concediul de maternitate are o durată fixă prin lege, iar indemnizația se calculează după o formulă clară, raportată la veniturile din ultimele 6 luni.

## Temeiul legal

::: ghid-temei
„ART. 23 (1) Asiguratele au dreptul la concedii pentru sarcină și lăuzie, pe o perioadă de 126 de zile calendaristice, perioadă în care beneficiază de indemnizație de maternitate.

ART. 25 (1) Cuantumul brut lunar al indemnizației de maternitate este de 85% din baza de calcul stabilită conform art. 10."
— OUG 158/2005 privind concediile și indemnizațiile de asigurări sociale de sănătate, art. 23 alin. (1) și art. 25 alin. (1) (sursă: anaf_surse/oug_158_2005_consolidat.txt)
:::

Elementele de calcul rezultă din text și din articolele conexe:

- **Durata totală** a concediului de maternitate este de **126 de zile calendaristice**, împărțită de regulă în 63 de zile de concediu prenatal (sarcină) și 63 de zile postnatal (lăuzie) — cu posibilitatea compensării între ele, cu condiția ca lăuzia să nu scadă sub 42 de zile.
- **Cuantumul indemnizației este 85% din baza de calcul**, nu din salariul brut integral.
- Baza de calcul se determină, potrivit art. 10, ca **medie a veniturilor brute lunare din ultimele 6 luni** din cele 12 luni care constituie stagiul de asigurare, plafonată la 12 salarii minime brute pe țară lunar.
- Indemnizația de maternitate este **neimpozabilă** și, potrivit regulilor generale aplicate acestei categorii de venituri, se exceptează de la unele contribuții — un tratament diferit față de salariul obișnuit.

## Ce se greșește în practică

- Se calculează indemnizația ca 85% din ultimul salariu brut, în loc de media veniturilor brute din ultimele 6 luni din cele 12 luni de stagiu.
- Se aplică incorect plafonarea la 12 salarii minime brute pe țară, fie omițând-o, fie aplicând-o pe o bază greșită.
- Se tratează indemnizația de maternitate ca fiind impozabilă și supusă acelorași contribuții ca salariul obișnuit.

## Ce face iConta.eu

Am verificat în `core/salarizare.py`: aplicația **calculează automat indemnizația de maternitate** (codul de concediu „08"), aplicând cota de 85% prevăzută de art. 25 alin. (1) din OUG 158/2005 (linia care mapează codurile „08" — maternitate — și „09" — îngrijire copil — la procentul de 0,85), tratează suma ca neimpozabilă conform art. 62 lit. c) din Codul fiscal și aplică regulile specifice de contribuții (CAS 25% uniform, CASS scutit pentru acest cod). Calculul bazei pe cele 6 luni de referință și plafonarea la 12 salarii minime se fac pe baza datelor introduse de contabil despre veniturile anterioare ale salariatei.

[iConta.eu](/)
