---
title: "Ce legătură există între PFA-ul asociatului și plafonul micro al SRL-ului?"
description: "Codul fiscal impune cumularea veniturilor PFA-ului unui asociat cu peste 25% din SRL cu veniturile firmei, la verificarea plafonului de microîntreprindere."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce legătură există între PFA-ul asociatului și plafonul micro al SRL-ului?

Un asociat care deține și un SRL la micro, și un PFA activ, nu poate trata cele două entități izolat pentru verificarea plafonului de venituri — legea impune, explicit, cumularea lor, în anumite condiții de deținere.

## Temeiul legal

::: ghid-temei
„Persoana juridică română care verifică condiția [dacă] are unul sau mai mulți acționari/asociați care dețin, direct și/sau indirect, peste 25% din valoarea/numărul titlurilor de participare sau al drepturilor de vot ale acestei persoane juridice române, acționari/asociați care desfășoară și activitate economică prin intermediul unei persoane fizice autorizate/întreprinderi individuale/întreprinderi familiale/altei forme de organizare a unei activități economice, fără personalitate juridică, autorizată potrivit legilor în vigoare. În această situație, veniturile înregistrate potrivit reglementărilor contabile aplicabile sau norma anuală de venit [...] ale/a persoanei fizice autorizate [...] se cumulează cu cele realizate de persoana juridică română."
— Legea nr. 227/2015 (Codul fiscal), art. 47 alin. (1^1) lit. d) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă, concret, această legătură:

- Dacă un asociat deține **peste 25%** din titlurile de participare sau drepturile de vot ale SRL-ului și, în același timp, **desfășoară și activitate printr-un PFA** (sau întreprindere individuală/familială), veniturile PFA-ului se **cumulează** cu veniturile SRL-ului pentru verificarea plafonului de micro (100.000 euro din 2026).
- Venitul PFA-ului luat în calcul este cel înregistrat potrivit contabilității în partidă simplă sau, dacă e cazul, **norma anuală de venit** aplicabilă acelui PFA — nu doar veniturile efectiv încasate, în funcție de sistemul de impunere ales de PFA.
- Dacă suma celor două (venituri SRL + venituri/norma PFA) depășește plafonul de micro, SRL-ul poate ieși din regimul micro, chiar dacă, privite izolat, veniturile proprii ale SRL-ului nu ar depăși plafonul.
- Pragul de deținere de 25% este cel care declanșează obligația de cumulare — un asociat cu o cotă mai mică nu generează, prin PFA-ul propriu, această legătură fiscală.

## Ce se greșește în practică

- Se verifică plafonul de micro strict pe baza cifrei de afaceri a SRL-ului, ignorând veniturile PFA-ului unui asociat majoritar (peste 25%), deși legea cere expres cumularea.
- Se presupune că regula se aplică doar dacă asociatul e administrator sau lucrează efectiv în firmă, deși criteriul legal este procentul de deținere a titlurilor de participare/drepturilor de vot, nu implicarea operațională.
- Se ignoră faptul că, pentru un PFA la normă de venit, se cumulează norma anuală (o sumă fixă), nu veniturile reale efectiv încasate, care pot fi mult diferite.

## Ce face iConta.eu

iConta.eu nu calculează sau verifică automat plafonul de încadrare la micro — nu există, la acest moment, o constantă sau un modul dedicat verificării plafonului de 100.000 euro; aplicația calculează doar baza impozabilă trimestrială (cota de 1%), din veniturile firmei gestionate. Cumularea cu veniturile unui PFA al asociatului, atunci când acesta deține peste 25% din SRL, presupune oricum date dintr-o entitate separată (PFA-ul), care nu este neapărat gestionată în același cont iConta.eu — verificarea și cumularea acestor venituri externe rămân, prin natura lor, responsabilitatea utilizatorului/contabilului.

[iConta.eu](/)
