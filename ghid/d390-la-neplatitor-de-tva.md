---
title: D390 la un neplătitor de TVA: când se depune și ce conține
description: Un neplătitor înregistrat prin art. 317 depune declarația recapitulativă D390 pentru achizițiile intracomunitare de bunuri (cod A) și pentru serviciile primite conform art. 278 alin. (2) (cod S), până pe 25 a lunii următoare, numai pentru lunile cu operațiuni (art. 325 din Codul fiscal).
published: 2026-08-24
modified: 2026-08-24
---

# D390 la un neplătitor de TVA: când se depune și ce conține

Declarația recapitulativă nu e rezervată plătitorilor de TVA. O firmă înregistrată special prin art. 317 o depune pentru operațiunile ei intracomunitare, chiar dacă nu colectează și nu deduce TVA.

### Ce intră

Lista din art. 325 din Codul fiscal e închisă:

| Cod | Operațiunea |
|---|---|
| L | Livrări intracomunitare de bunuri |
| A | Achiziții intracomunitare de bunuri |
| S | Prestări și achiziții de servicii intracomunitare, art. 278 alin. (2) |
| T | Livrări în cadrul unei operațiuni triunghiulare |
| P | Achiziții în cadrul unei operațiuni triunghiulare |
| R | Livrări intracomunitare efectuate de agricultori în regim special |

Pentru un neplătitor înregistrat prin art. 317, în practică apar **A** și **S**.

### Ce nu intră

- operațiunile de tip 4 din D301 — art. 307 alin. (3), (5) și (6) — fiindcă nu sunt operațiuni intracomunitare;
- achizițiile intracomunitare de mijloace de transport noi, care au regim de raportare propriu;
- importurile și livrările către state din afara UE.

### Termenul

25 a lunii următoare. D390 e **lunară pentru toată lumea**, indiferent de perioada fiscală la TVA. Un plătitor cu decont trimestrial depune tot D390 lunar.

Ca și D301, se depune numai pentru lunile în care există operațiuni.

### Codul de TVA al partenerului

E câmpul care produce cele mai multe respingeri. Validatorul ANAF verifică algoritmul specific fiecărei țări — cifra de control diferă de la un stat la altul, la fel cum CUI-ul românesc are propriul algoritm.

Un cod inventat sau tastat greșit trece de o verificare de lungime, dar pică la validare cu regula **R24.1**. Verificarea în VIES înainte de operațiune rezolvă problema la sursă: dacă furnizorul nu are cod valid, nu există livrare intracomunitară scutită, iar el ar fi trebuit să factureze cu TVA.

Codul se înscrie **fără prefixul de țară** — prefixul se completează în câmpul separat de țară.

### Corelarea cu D301

Aceeași achiziție apare în ambele declarații, cu roluri diferite. Bazele trebuie să coincidă pentru operațiunile care intră în amândouă. Diferența legitimă vine doar din operațiunile de tip 2 și tip 4, care sunt în D301 dar nu în D390.

O diferență neexplicată înseamnă că o operațiune a fost clasificată greșit — cel mai probabil un serviciu pus ca tip 4.

### Ce face iConta

Derivă D390 din operațiunile D301, cu maparea explicită tip 1 și 3 → A, tip 5 → S. Fiecare operațiune exclusă apare în diagnostic cu motivul, nu dispare tăcut. Codul de TVA e verificat algoritmic la introducere și la generare, pentru țările cu algoritm cunoscut offline; restul se deferă validatorului, dar cu semnal, nu cu tăcere.
