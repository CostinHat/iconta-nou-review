---
title: Salariul brut vs net pentru un salariat cu deducere personală?
description: Deducerea personală reduce baza de calcul a impozitului, nu contribuțiile CAS/CASS, iar valoarea ei scade degresiv pe măsură ce brutul crește peste salariul minim, în funcție de numărul persoanelor aflate în întreținere.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Salariul brut vs net pentru un salariat cu deducere personală?

Deducerea personală este suma care se scade din baza de calcul a impozitului pe venit, înainte de aplicarea cotei de 10%. Nu reduce CAS sau CASS, ci doar impozitul, iar valoarea ei nu este fixă — depinde de nivelul salariului brut și de numărul persoanelor aflate în întreținere.

## Temeiul legal

::: ghid-temei
**Codul fiscal, Articolul 77, alin.(3):** *"Deducerea personală de bază se acordă pentru persoanele fizice care au un venit lunar brut de până la 2.000 de lei peste nivelul salariului de bază minim brut pe țară garantat în plată... În situația în care, în cursul aceleiași luni, se utilizează mai multe valori ale salariului minim brut pe țară, se ia în calcul valoarea cea mai mică a salariului minim brut pe țară."*

**Codul fiscal, Articolul 77, alin.(10) lit.a):** *"15% din salariul de bază minim brut pe țară garantat în plată pentru persoanele fizice cu vârsta de până la 26 de ani, care realizează venituri din salarii al căror nivel este de până la nivelul prevăzut la alin. (3)"*

**Codul fiscal, Articolul 77, alin.(10) lit.b):** *"100 de lei lunar pentru fiecare copil cu vârsta de până la 18 ani, dacă acesta este înscris într-o unitate de învățământ, părintelui care realizează venituri din salarii, indiferent de nivelul acestora"*

**Codul fiscal, Articolul 77, alin.(12)/(13):** *"...prin prezentarea documentului care atestă înscrierea copilului într-o unitate de învățământ și a unei declarații pe propria răspundere din partea părintelui beneficiar"* + declarația de neconcurs la alt angajator.
:::

## Cum se calculează deducerea

Deducerea personală se acordă doar salariaților al căror venit brut lunar nu depășește salariul minim plus 2.000 lei — peste acest plafon, deducerea este zero. Sub plafon, deducerea de bază pornește de la un procent din salariul minim, în funcție de numărul persoanelor aflate în întreținere (0, 1, 2, 3 sau 4 și peste), și scade progresiv pe măsură ce brutul crește peste salariul minim, cu 0,5 puncte procentuale la fiecare tranșă de 50 de lei (sau fracție) peste salariul minim.

La acestea se pot adăuga două sume suplimentare, dacă se îndeplinesc condițiile legale:

- **+15% din salariul minim**, pentru salariați cu vârsta sub 26 de ani, dar numai dacă brutul se încadrează în același plafon (salariul minim + 2.000 lei);
- **+100 lei/lună pentru fiecare copil școlarizat** (sub 18 ani, înscris într-o unitate de învățământ) — dar legea condiționează acordarea acestei sume de o declarație pe propria răspundere a părintelui și de documentul care atestă înscrierea la școală. Fără declarație, deducerea suplimentară nu se poate acorda tacit.

::: ghid-exemplu
Un salariat fără persoane în întreținere, cu brut de 4.325 lei (exact salariul minim din 2026 H2), primește deducerea de bază la nivelul maxim al tranșei (20% din salariul minim pentru 0 persoane în întreținere). Dacă brutul crește cu 150 lei peste salariul minim, deducerea scade cu 3 tranșe de 0,5 puncte procentuale (rotunjite în sus), adică 1,5 puncte procentuale mai puțin față de nivelul maxim.
:::

## Ce se greșește în practică

- Se aplică deducerea personală și peste plafonul de salariul minim + 2.000 lei, unde legea prevede deducere zero.
- Se calculează scăderea procentuală pe tranșe de 50 lei prin rotunjire în jos, în loc de rotunjire în sus — diferența poate acorda eronat o deducere mai mare decât cea legală pe o parte din valorile de brut ale fiecărei tranșe.
- Se acordă deducerea de 100 lei/copil școlarizat fără declarația pe propria răspundere a părintelui, deși legea o cere explicit ca o condiție pentru acordare.
- Se confundă deducerea personală (care reduce doar baza de impozit) cu o reducere a CAS sau CASS — deducerea nu afectează aceste contribuții.
- Se rotunjește suma deducerii calculate, deși legea prevede rotunjirea doar a perioadei de acordare, nu a sumei.

## Ce face iConta.eu

Funcția de calcul al deducerii personale aplică plafonul „salariul minim + 2.000 lei" peste care deducerea devine zero, scara degresivă pe persoane în întreținere (0/1/2/3/4 și peste), scăderea de 0,5 puncte procentuale pe fiecare tranșă de 50 lei peste salariul minim (rotunjire în sus la calculul tranșei), plus bonusul de 15% pentru salariați sub 26 de ani atunci când brutul se încadrează în plafon. Suma deducerii nu este rotunjită. Pentru deducerea suplimentară de 100 lei/copil școlarizat, motorul de calcul respinge explicit calculul dacă parametrul privind numărul de copii școlarizați este completat fără bifarea declarației cerute de părinte — corect, conform legii. Menționăm însă că, la momentul actual, acest parametru specific (copii școlarizați) nu este încă legat la niciun câmp din interfața aplicației — este o funcționalitate pregătită în motorul de calcul, dar nu încă disponibilă efectiv utilizatorului final.

[iConta.eu](/)
