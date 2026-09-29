---
title: "Sumele imputate angajaților pentru lipsuri din gestiune se colectează cu TVA?"
description: "Nu. Sumele imputate pentru bunurile lipsă nu sunt contravaloarea unei operațiuni în sfera TVA; separat, TVA dedusă la bunurile lipsă se ajustează dacă lipsa nu e o excepție legală."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Sumele imputate angajaților pentru lipsuri din gestiune se colectează cu TVA?

Nu. Când se constată lipsuri în gestiune și suma se impută gestionarului sau altui angajat vinovat, **suma imputată nu este contravaloarea unei livrări** și nu intră în sfera TVA. Nu se colectează TVA pe ea. Regula e aceeași indiferent dacă pentru bunurile lipsă este sau nu obligatorie ajustarea TVA dedusă.

Ajustarea e însă o problemă separată. Bunurile lipsă din alte cauze decât distrugerea, pierderea sau furtul dovedite corespunzător nu mai sunt folosite pentru operațiuni taxabile. TVA dedusă la achiziția lor se ajustează, adică se anulează. Imputarea recuperează paguba de la angajat, dar nu înlocuiește ajustarea.

## Temeiul legal

::: ghid-temei
„a) bunuri lipsă în gestiune din alte cauze decât cele prevăzute la art. 304 alin. (2) din Codul fiscal. În cazul bunurilor lipsă din gestiune care sunt imputate, sumele imputate nu sunt considerate contravaloarea unor operațiuni în sfera de aplicare a TVA, indiferent dacă pentru acestea este sau nu obligatorie ajustarea taxei;"
— Normele metodologice ale Codului fiscal (HG 1/2016), Titlul VII, pct. 78 alin. (6) lit. a) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)

„În cazul bunurilor lipsă din gestiune, altele decât cele prevăzute la art. 305 alin. (4) lit. d) pct. 1 și 2 din Codul fiscal, care sunt imputate, sumele imputate nu sunt considerate contravaloarea unor operațiuni în sfera de aplicare a TVA, indiferent dacă pentru acestea este sau nu obligatorie ajustarea taxei."
— Normele metodologice ale Codului fiscal (HG 1/2016), Titlul VII, pct. 79 alin. (10) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

::: ghid-temei
„persoana impozabilă își pierde sau câștiga dreptul de deducere a taxei pentru bunurile mobile nelivrate și serviciile neutilizate."
— Codul fiscal (Legea 227/2015), art. 304 alin. (1) lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„bunurilor distruse, pierdute sau furate, în condițiile în care aceste situații sunt demonstrate sau confirmate în mod corespunzător de persoana impozabilă."
— Codul fiscal (Legea 227/2015), art. 304 alin. (2) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cele două întrebări, separat:

- **Se colectează TVA pe suma imputată? Nu.** Normele spun expres, atât pentru stocuri (pct. 78), cât și pentru bunurile de capital (pct. 79), că sumele imputate nu sunt contravaloarea unor operațiuni în sfera TVA. Nu se emite factură cu TVA către angajat pentru imputare.
- **Se ajustează TVA dedusă la bunurile lipsă? De regulă, da.** Lipsa din alte cauze decât cele de la art. 304 alin. (2) atrage ajustarea deducerii (pct. 78 alin. (6) lit. a)). Nu se ajustează doar dacă bunurile sunt distruse, pierdute sau furate, iar situația e demonstrată corespunzător. Pentru furt e nevoie de acte ale organelor judiciare.
- **Bunuri de capital.** La un bun de capital lipsă, ajustarea se face după art. 305 alin. (4) lit. d) din Codul fiscal, pentru taxa aferentă perioadei rămase din perioada de ajustare. Și aici imputarea rămâne în afara sferei TVA (pct. 79 alin. (10)).
- **Cota ajustării** este cea în vigoare la data achiziției bunurilor (pct. 78 alin. (13) din norme).

::: ghid-exemplu
La inventarul SC Exemplu SRL se constată lipsă marfă cumpărată cu 1.000 lei plus TVA 21% (210 lei), dedusă integral. Lipsa nu are o cauză dovedită de distrugere, pierdere sau furt. Suma se impută gestionarului.

- TVA colectată pe suma imputată: 0 lei. Imputarea nu e operațiune în sfera TVA.
- Ajustarea TVA dedusă: 210 lei, care nu mai sunt deductibili.
- Suma imputată gestionarului se stabilește potrivit regulilor de răspundere materială. Ea nu devine bază de TVA.
:::

## Ce se greșește în practică

- Se emite factură cu TVA către angajat pentru suma imputată. Normele spun că suma nu e contravaloarea unei operațiuni în sfera TVA.
- Se consideră că, dacă paguba se recuperează de la angajat, nu mai trebuie ajustată TVA dedusă. Imputarea și ajustarea sunt independente.
- Se aplică scutirea de ajustare pentru o lipsă simplă, fără dovada distrugerii, pierderii sau furtului.
- La bunurile de capital lipsă, se ajustează doar o cincime, deși pentru încetarea existenței bunului ajustarea privește toată perioada rămasă.

## Ce face iConta.eu

Modulul de inventariere din iConta.eu generează notele pentru minusurile constatate: descărcarea gestiunii, imputarea către salariat sau terț și ajustarea TVA dedusă. Pentru minusul imputabil, nota propusă nu include TVA colectată pe suma imputată — suma imputată nu e în sfera TVA. În schimb, aplicația înregistrează ajustarea TVA dedusă la bunurile lipsă din gestiune (635 = 4426), calculată pe costul bunului, cât timp nu se aplică excepțiile de la art. 304 alin. (2) (bun asigurat sau distrus dovedit). Verificarea aplicării excepției rămâne a contabilului.

[iConta.eu](/)
