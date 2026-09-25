---
title: "Cum se calculează amortizarea la bunurile în regim de antrepozit"
description: "Explicație onestă a regulilor de amortizare fiscală și a motivului pentru care nu există un regim special de amortizare pentru bunurile aflate într-un antrepozit fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează amortizarea la bunurile în regim de antrepozit

Întrebarea ascunde de fapt o confuzie destul de răspândită: „antrepozitul fiscal" e un regim de **accize** (taxă specială pe alcool, tutun, produse energetice), nu o categorie specială de active amortizabile. Codul fiscal nu leagă niciodată amortizarea de faptul că un bun stă depozitat într-un antrepozit — leagă amortizarea de faptul că bunul e un **mijloc fix**, indiferent unde e ținut.

## Temeiul legal

::: ghid-temei
„(1) Cheltuielile aferente achiziționării, producerii, construirii mijloacelor fixe amortizabile, precum și investițiile efectuate la acestea se recuperează din punct de vedere fiscal prin deducerea amortizării potrivit prevederilor prezentului articol.
(2) Mijlocul fix amortizabil este orice imobilizare corporală care îndeplinește cumulativ următoarele condiții: a) este deținut și utilizat în producția, livrarea de bunuri sau în prestarea de servicii, pentru a fi închiriat terților sau în scopuri administrative; [...] b) la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei [...]; c) are o durată normală de utilizare mai mare de un an."
— Legea nr. 227/2015 (Codul fiscal), art. 28 alin. (1)-(2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Amortizarea fiscală se aplică exclusiv **mijloacelor fixe** — active folosite în activitatea proprie (producție, livrare de bunuri, prestare de servicii, închiriere sau scop administrativ), cu valoare de minimum 5.000 lei și durată de utilizare peste un an.
- „Antrepozitul fiscal" e definit separat, în Titlul VIII al Codului fiscal (accize): „antrepozit fiscal reprezintă un loc în care produsele accizabile sunt produse, transformate, deținute, depozitate, primite sau expediate în regim suspensiv de accize de către un antrepozitar autorizat" — art. 336 pct. 3 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt, linia 22802). E o categorie de **suspendare a exigibilității accizei**, complet independentă de art. 28.
- Metoda de amortizare (liniară, degresivă, accelerată sau superaccelerată din 2026) depinde de **categoria mijlocului fix** — construcții, echipamente tehnologice, alte active — conform art. 28 alin. (5), niciodată de locul fizic în care se află bunul.

## Ce se greșește în practică

- Se presupune că mărfurile/produsele accizabile ținute mult timp într-un antrepozit fiscal (alcool, tutun, carburanți) devin „mijloace fixe" doar pentru că stau depozitate — de fapt, cât timp sunt destinate vânzării, rămân **stocuri**, nu active amortizabile; stocurile nu se amortizează, ci se scad din gestiune la vânzare/consum.
- Se caută în lege un „regim special de amortizare pentru antrepozit" care pur și simplu nu există — combinarea celor doi termeni („antrepozit" + „amortizare") nu are corespondent normativ; sunt două instituții fiscale diferite (accize vs. impozit pe profit).
- Se aplică regulile de amortizare (prag 5.000 lei, durată peste 1 an) unor bunuri care de fapt sunt marfă de vânzare aflată temporar sub regim suspensiv de acciză, nu imobilizări corporale.

## Ce face iConta.eu

iConta.eu are un motor real de amortizare fiscală (evidența mijloacelor fixe, cu metodă liniară, degresivă, accelerată și superaccelerată, calculată conform art. 28 alin. (5)-(8^1) din Codul fiscal, inclusiv reevaluări aplicate pe parcurs). Motorul lucrează exclusiv cu mijloace fixe înregistrate ca atare (valoare, durată normală de funcționare, dată de punere în funcțiune, metodă) — nu are, și nu are de ce să aibă, vreo logică separată pentru „bunuri în regim de antrepozit": în cod nu există nicio asociere între antrepozitul fiscal (accize) și modulul de amortizare. Dacă firma ține bunuri accizabile în antrepozit ca marfă de vânzare, acelea intră în gestiunea de stocuri a aplicației, nu în evidența mijloacelor fixe.

[iConta.eu](/)
