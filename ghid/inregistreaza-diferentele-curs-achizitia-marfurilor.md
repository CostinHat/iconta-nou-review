---
title: "Cum se înregistrează diferențele de curs la achiziția mărfurilor?"
description: "Marfa achiziționată în valută se înregistrează o singură dată, la cursul din ziua recepției — costul ei nu generează diferențe de curs ulterioare, spre deosebire de datoria față de furnizor."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează diferențele de curs la achiziția mărfurilor?

La achiziția de marfă în valută nu apare, propriu-zis, nicio „diferență de curs la achiziție" — marfa se înregistrează o singură dată, la cursul de schimb din ziua operațiunii, iar acel cost rămâne fix. Ce se poate mișca ulterior e datoria față de furnizor, dacă rămâne neachitată — dar aceea e o operațiune separată de achiziția mărfii în sine.

## Temeiul legal

::: ghid-temei
„319. - O tranzacție în valută trebuie înregistrată inițial la cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunii."
— OMFP 1802/2014, Reglementările contabile, pct. 319 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Corelat cu definiția elementelor nemonetare de la pct. 315 alin. (3) din aceleași reglementări — care numește explicit „stocurile" printre exemplele de elemente nemonetare — rezultă mecanismul complet:

- **Marfa** intră în gestiune la costul stabilit o singură dată, la cursul BNR din ziua recepției (pct. 319). Nu se recalculează ulterior în funcție de curs.
- **Datoria față de furnizor**, rezultată din aceeași achiziție, e însă un element monetar. Dacă rămâne neachitată la finalul lunii, se reevaluează la cursul BNR din ultima zi bancară a lunii; iar la momentul plății efective, orice diferență între cursul din evidență și cursul zilei plății se recunoaște ca venit sau cheltuială din diferențe de curs (665/765).

Deci „diferența de curs la achiziția mărfurilor" din titlu, interpretată corect, nu privește costul mărfii, ci datoria comercială generată de acea achiziție.

## Ce se greșește în practică

- Se ajustează costul de intrare al mărfii la finalul lunii, pe baza cursului BNR curent, ca și cum marfa ar fi un element monetar — nu e cazul, costul rămâne fix de la recepție.
- Se omite reevaluarea lunară a datoriei către furnizorul extern, dacă rămâne neachitată — aici chiar apare o diferență de curs reală, doar că nu ține de marfa în sine.
- Se calculează „diferența" comparând cursul de la recepție cu cursul de la data plății direct pe valoarea mărfii, în loc să se trateze separat costul mărfii (fix) și diferența de curs de la decontarea datoriei (variabilă).

## Ce face iConta.eu

iConta.eu tratează marfa ca element nemonetar: motorul de diferențe de curs (folosit pentru decontarea și reevaluarea lunară a creanțelor, datoriilor și disponibilităților în valută) acceptă explicit doar aceste trei tipuri și respinge orice tentativă de a introduce „stoc" ca obiect al calculului — deci costul mărfii nu poate fi, structural, atins de acest motor.

Ce acoperă aplicația, separat: dacă achiziția de marfă generează o datorie față de un furnizor extern rămasă neachitată, acea datorie poate fi introdusă în funcționalitatea de reevaluare lunară (la finalul lunii) sau de decontare (la plata efectivă) — ambele calculează automat 665/765 pe baza cursului BNR. Costul mărfii propriu-zise nu e, și nu trebuie să fie, atins de acest calcul.

[iConta.eu](/)
