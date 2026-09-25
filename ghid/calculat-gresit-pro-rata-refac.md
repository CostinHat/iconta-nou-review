---
title: "Am calculat greșit pro-rata: cum o refac"
description: "Cum se recalculează corect pro-rata de TVA pentru un an fiscal, dacă a fost aplicată greșit pro-rata provizorie sau cea definitivă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Am calculat greșit pro-rata: cum o refac

Dacă ați dedus TVA pe baza unei pro-rate provizorii greșite sau nu ați efectuat regularizarea de sfârșit de an cu pro-rata definitivă, corectarea nu se face „din ochi" — legea stabilește exact ce se compară și unde se înscrie diferența.

## Temeiul legal

::: ghid-temei
„(12) Taxa de dedus pentru un an calendaristic se calculează definitiv prin înmulțirea sumei totale a taxei deductibile din anul calendaristic respectiv, prevăzută la alin. (5), cu pro rata definitivă prevăzută la alin. (8), determinată pentru anul respectiv. [...]
(14) La sfârșitul anului, persoanele impozabile cu regim mixt trebuie să ajusteze taxa dedusă provizoriu [...] astfel: a) din taxa de dedus determinată definitiv, conform alin. (12), se scade taxa dedusă într-un an, determinată pe bază de pro rata provizorie; b) rezultatul diferenței de la lit. a), în plus sau în minus după caz, se înscrie în rândul de regularizări din decontul de taxă [...] aferent ultimei perioade fiscale a anului."
— Cod fiscal, art. 300 alin. (12) și (14) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Refacerea corectă a calculului urmează pașii din articol:

- **Recalculați pro-rata definitivă** a anului: raportul dintre operațiunile cu drept de deducere și totalul operațiunilor (cu și fără drept de deducere), rotunjit la cifra întreagă imediat următoare.
- **Recalculați taxa de dedus definitivă**: suma totală a TVA deductibile din an (pentru achizițiile mixte) înmulțită cu pro-rata definitivă corectă.
- **Comparați cu ce ați dedus deja** pe bază de pro-rata provizorie (cea aplicată lună de lună/trimestru de trimestru).
- **Înscrieți diferența** (plus sau minus) ca regularizare, în decontul de TVA aferent **ultimei perioade fiscale a anului** — nu într-un decont oarecare, ulterior, ales la întâmplare.
- Dacă eroarea a rămas nedescoperită și decontul respectiv a fost deja depus, corectarea se face prin decont rectificativ pentru acea perioadă (ultima perioadă fiscală a anului în cauză).
- Pentru bunurile de capital (mijloace fixe) la care s-a aplicat pro-rata definitivă, ajustările din anii următori se fac separat, pe o cincime (bunuri mobile) sau o douăzecime (bunuri imobile) din perioada de ajustare — nu se reface tot dintr-o dată.

## Ce se greșește în practică

- Se aplică pro-rata definitivă a anului anterior ca pro-rata provizorie pentru anul curent, dar se uită complet regularizarea de la finalul anului curent cu pro-rata definitivă proprie acestuia.
- Se înscrie diferența de regularizare într-un decont ales arbitrar, nu în cel al ultimei perioade fiscale a anului, cum cere legea.
- Se recalculează greșit rotunjirea pro-ratei — legea cere rotunjire „până la cifra unităților imediat următoare" (adică întotdeauna în sus), nu rotunjire matematică standard.
- Se omit din calcul excluderile obligatorii (de exemplu valoarea livrărilor de bunuri de capital sau operațiunile imobiliare accesorii), ceea ce denaturează atât numărătorul, cât și numitorul fracției.

## Ce face iConta.eu

iConta.eu permite introducerea manuală a pro-ratei (`pro_rata`) în profilul fiscal al firmei, valoare care e apoi folosită la generarea D300: dacă e sub 100%, aplicația calculează automat ajustarea corespunzătoare pe rândul de regularizare al deconturilor. La data acestui ghid, iConta.eu **nu calculează automat pro-rata definitivă** din operațiunile firmei (numărător/numitor conform art. 300 alin. (6)) — procentul rămâne o valoare pe care contabilul o determină și o introduce, pe răspunderea lui, conform metodologiei din articol; aplicația doar aplică procentul introdus la generarea declarației.

[iConta.eu](/)
