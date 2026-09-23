---
title: "Ce fac dacă am aplicat taxarea inversă greșit?"
description: "Neaplicarea corectă a taxării inverse potrivit art. 331 CF poate duce la pierderea dreptului de deducere al beneficiarului — norma metodologică descrie exact acest caz."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă am aplicat taxarea inversă greșit?

Cea mai gravă consecință documentată în lege pentru o greșeală legată de taxarea inversă internă
(art. 331 CF) nu este o amendă, ci pierderea dreptului de deducere al beneficiarului — și se
întâmplă exact în situația în care furnizorul trebuia să aplice taxarea inversă, dar a facturat cu
TVA.

## Temeiul legal

::: ghid-temei
„(4) În cazul neaplicării taxării inverse prevăzute de lege, respectiv în situația în care
furnizorul/prestatorul emite o factură cu TVA pentru operațiunile prevăzute la art. 331 alin. (2)
din Codul fiscal și nu înscrie mențiunea „taxare inversă" în respectiva factură, iar beneficiarul
deduce taxa înscrisă în factură, acesta își pierde dreptul de deducere pentru achiziția respectivă
de bunuri sau servicii deoarece condițiile de fond privind taxarea inversă nu au fost respectate și
factura a fost întocmită în mod eronat. Aceste prevederi se aplică și în situația în care
îndreptarea respectivei erori nu este posibilă din cauza falimentului furnizorului/prestatorului."

— pct. 109 alin. (4) din normele metodologice (HG 1/2016)
:::

Câteva puncte de reținut din acest text:

- Se aplică pentru operațiunile care se încadrau, de fapt, la una din cele 12 categorii de la
  art. 331 alin. (2) (deșeuri, masă lemnoasă, cereale, certificate de emisii, energie electrică,
  certificate verzi, clădiri/terenuri, aur de investiții, telefoane, circuite integrate,
  console/tablete/laptopuri, gaze naturale), dar furnizorul a facturat greșit cu TVA, fără mențiunea
  „taxare inversă".
- Consecința cade pe **beneficiar**: pierde dreptul de deducere pentru taxa dedusă greșit din acea
  factură.
- Norma este explicită: pierderea dreptului de deducere se aplică **și dacă** furnizorul a intrat
  între timp în faliment și eroarea nu mai poate fi corectată printr-o factură rectificativă.

Practic, prima linie de apărare este corectarea rapidă a facturii: furnizorul emite o factură
rectificativă fără TVA, cu mențiunea „taxare inversă", iar beneficiarul își ajustează deducerea și
înregistrează operațiunea corect, prin formula 4426=4427 (pct. 109 alin. (1) din norme).

## Ce se greșește în practică

Greșeala de bază este identificarea greșită a categoriei operațiunii — fie tratarea unei operațiuni
care nu se încadrează la art. 331 alin. (2) ca taxare inversă (fără temei), fie, invers, facturarea
cu TVA a unei operațiuni care se încadra la una dintre cele 12 categorii. A doua situație e cea
descrisă explicit de norma citată mai sus și e cea cu consecința cea mai gravă pentru beneficiar.

O altă sursă de eroare, la nivel de evidență, este introducerea aceleiași sume atât automat (din
factură), cât și manual, în rândurile de decont dedicate taxării inverse — ceea ce duce la dublarea
sumei raportate.

## Ce face iConta.eu

Motorul de taxare inversă din aplicație validează, înainte de a permite operațiunea, patru condiții
în ordine: categoria trebuie să fie una dintre cele 12 recunoscute de lege, ambele părți trebuie să
fie plătitoare de TVA, categoria să nu fi expirat la data operațiunii și, dacă e cazul, suma să
depășească pragul legal — altfel operațiunea este respinsă cu un mesaj explicit al motivului.
Pentru declarația D300, aplicația are o gardă separată împotriva dublei numărări: dacă aceeași sumă
este introdusă și automat din factură, și manual în rândurile dedicate taxării inverse (rd. 12/13/25),
calculul decontului este blocat cu un mesaj de eroare care semnalează dubla înregistrare. La D394 nu
există aceeași gardă explicită — operațiunile automate (din facturi) și cele introduse manual se
însumează pe aceeași cheie, fără o verificare dedicată de duplicat.

[iConta.eu](/)
