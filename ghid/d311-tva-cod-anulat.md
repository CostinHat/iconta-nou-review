---
title: D311: TVA de plată după anularea codului de TVA
description: Ce declari prin D311 după ce ANAF îți anulează codul de TVA potrivit art. 316 alin. (11), ce operațiuni intră și de ce obligația de a colecta TVA nu dispare odată cu codul.
published: 2026-08-13
modified: 2026-08-13
---

# Ce declari prin D311 după ce ți s-a anulat codul de TVA?

Anularea codului de TVA nu te scutește de TVA. Continui să datorezi taxa pe livrările și prestările făcute după anulare — doar că nu o mai poți declara prin decontul obișnuit, pentru că decontul se depune doar de cei înregistrați. Pentru asta există D311: declarația prin care persoanele cu cod anulat își declară TVA-ul colectat. Cine crede că, fără cod, nu mai are obligații de TVA, acumulează datorie fără să știe.

## Temeiul legal

::: ghid-temei
**Art. 11 alin. (6) și (8) din Codul fiscal (Legea 227/2015)** — persoanele impozabile cărora li s-a anulat înregistrarea în scopuri de TVA potrivit art. 316 alin. (11) **nu beneficiază de dreptul de deducere** a taxei aferente achizițiilor efectuate în perioada respectivă, dar **sunt supuse obligației de plată a TVA colectate**, în conformitate cu prevederile titlului VII, pentru operațiunile taxabile efectuate în acea perioadă.

**Art. 316 alin. (11) din Codul fiscal** — cazurile în care organul fiscal anulează din oficiu înregistrarea în scopuri de TVA: inactivitate declarată, inactivitate temporară înscrisă la registrul comerțului, nedepunerea deconturilor, neevidențierea de operațiuni în deconturi, risc fiscal ridicat și celelalte situații enumerate în text.

Formularul **D311 — „Declarație privind taxa pe valoarea adăugată colectată datorată de către persoanele impozabile al căror cod de înregistrare în scopuri de taxă pe valoarea adăugată a fost anulat"** este aprobat prin ordin al președintelui ANAF, cu structura XML publicată de ANAF.
:::

## Regula concretă

**Cine depune.** Persoanele impozabile cărora li s-a anulat codul de TVA din oficiu, potrivit art. 316 alin. (11), și care efectuează operațiuni taxabile în perioada în care nu au cod.

**Ce se declară.** TVA-ul **colectat** pe operațiunile taxabile din perioada fără cod. Asimetria e importantă și e chiar mecanismul sancțiunii:

- **Colectezi și plătești** TVA pe livrările și prestările făcute.
- **Nu deduci** TVA pe achiziții, oricât ai plăti furnizorilor.

Anularea codului nu suspendă obligația de a colecta — suspendă doar dreptul de a deduce.

**Ce operațiuni intră.** Livrările de bunuri și prestările de servicii taxabile efectuate după data anulării, achizițiile pentru care ești obligat la plata taxei, ajustările de taxă și celelalte situații din structura declarației.

**Când se depune.** Până la data de 25 a lunii următoare celei în care a intervenit exigibilitatea taxei pentru operațiunile declarate.

**Ce urmează.** După reînregistrarea în scopuri de TVA, se revine la decontul obișnuit. Taxa nededusă în perioada fără cod poate fi recuperată în condițiile prevăzute de lege pentru reînregistrare — dar asta e o procedură separată, cu reguli proprii.

## Un exemplu

::: ghid-exemplu
**SC Exemplu SRL** are codul de TVA anulat din oficiu în martie 2026, pentru nedepunerea deconturilor.

**În aprilie 2026** firma continuă activitatea și emite facturi de **50.000 lei**, operațiuni taxabile la cota standard.

- **TVA colectată datorată:** 50.000 × 21% = **10.500 lei**
- Se declară prin **D311**, până la 25 mai 2026, și se plătește.

În aceeași lună, firma cumpără marfă de la furnizori și plătește **8.400 lei TVA** pe achiziții.

- **TVA deductibilă: 0 lei.** Fără cod de TVA, dreptul de deducere nu există.

**Rezultatul:** firma plătește 10.500 lei la buget și suportă 8.400 lei din achiziții ca simplu cost. Fără anularea codului, ar fi plătit doar diferența de 2.100 lei. Costul anulării, într-o singură lună, e de 8.400 lei.

Aici se vede de ce anularea codului nu e o formalitate administrativă, ci o problemă de trezorerie.
:::

## Ce se greșește în practică

- **Se crede că fără cod nu mai există TVA.** Obligația de a colecta rămâne. Ce dispare e dreptul de deducere.
- **Se emit facturi cu TVA ca înainte.** Facturarea în perioada fără cod are reguli proprii; TVA-ul se datorează, dar mențiunile de pe factură și tratamentul la client diferă.
- **Se așteaptă decontul.** Decontul de TVA se depune doar de cei înregistrați. În perioada fără cod, calea e D311.
- **Se ratează termenul.** Termenul e 25 a lunii următoare exigibilității, nu ritmul vechi al decontului.
- **Se ignoră cauza anulării.** Anularea vine dintr-un motiv — cel mai des, deconturi nedepuse. Cât timp cauza persistă, reînregistrarea nu e posibilă, iar costul se acumulează lunar.

## Ce face iConta.eu

iConta.eu generează D311 din operațiunile taxabile ale perioadei fără cod și produce fișierul XML validat pe **validatorul oficial ANAF (DUKIntegrator)**. Structura urmează schema în vigoare, determinată pe validator.

Aplicația tratează separat perioada fără cod: TVA-ul se colectează, dar nu se deduce pe achiziții — exact cum cere art. 11.

Depunerea o faci din SPV, cu fișierul deja verificat.

Vezi și: [decontul de TVA](/ghid/decont-tva-d300-rezultat), la care se revine după reînregistrare, și [cotele de TVA în vigoare](/ghid/cote-tva-2025).

[iConta.eu](/)
