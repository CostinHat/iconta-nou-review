---
title: "Cum se calculează plafonul zilnic pentru plățile în numerar?"
description: "Plafoanele zilnice de 5.000 lei și 10.000 lei din Legea 70/2015 se calculează per persoană/parteneră, nu per firmă, și interzic fragmentarea plăților."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează plafonul zilnic pentru plățile în numerar?

Legea 70/2015 nu stabilește un singur plafon zilnic, ci mai multe, în funcție de tipul operațiunii (încasare sau plată) și de tipul de partener (persoană juridică obișnuită sau magazin cash and carry). Confuzia dintre aceste plafoane, plus ignorarea interdicției de fragmentare, sunt cele mai frecvente greșeli.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile art. 1 alin. (1) se pot efectua operațiuni de încasări și plăți în numerar, în următoarele condiții: a) încasări de la persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei de la o persoană; [...] c) plăți către persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei/persoană, dar nu mai mult de un plafon total de 10.000 lei/zi; [...] e) plăți din avansuri spre decontare, în limita unui plafon zilnic de 5.000 lei, stabilit pentru fiecare persoană care a primit avansuri spre decontare."
— Legea 70/2015, art. 3 alin. (1) lit. a), c), e) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

- Plafonul de **5.000 lei/zi** se calculează **per partener** (per persoană juridică de la care se încasează sau către care se plătește), nu per firmă emitentă — dacă o firmă face plăți către mai mulți furnizori în aceeași zi, plafonul se verifică separat pentru fiecare furnizor.
- La plăți (nu la încasări), legea adaugă și un **plafon total zilnic de 10.000 lei**, indiferent de câți parteneri diferiți sunt plătiți în aceeași zi (art. 3 alin. 1 lit. c) — plafonul per-partener de 5.000 lei se combină cu acest plafon agregat.
- Pentru **magazinele de tip cash and carry**, plafoanele sunt duble: 10.000 lei/zi/persoană la încasare (lit. b) și 10.000 lei/zi în total la plată (lit. d).
- Plafonul pentru **avansuri spre decontare** e separat, de 5.000 lei/zi, calculat pentru fiecare persoană care a primit avans — iar suma respectivă intră în calculul plafonului zilnic din alin. (1) lit. c) sau d), după caz, chiar din momentul acordării avansului (art. 3 alin. 4).
- Legea interzice explicit **fragmentarea**: „sunt interzise încasările fragmentate în numerar de la beneficiari pentru facturile a căror valoare este mai mare de 5.000 lei [...], precum și fragmentarea facturilor" (art. 3 alin. 2) — nu se poate ocoli plafonul împărțind o factură mare în mai multe încasări/plăți mici.

## Ce se greșește în practică

- Se calculează plafonul per factură, în loc de per zi/per partener — o singură factură mare poate fi plătită parțial în numerar (până la 5.000 lei), restul obligatoriu prin instrument fără numerar, nu integral în numerar dacă depășește pragul.
- Se ignoră plafonul total zilnic de 10.000 lei la plăți, plătind câte 5.000 lei către mai mulți furnizori în aceeași zi, fără să verifice suma cumulată.
- Se tratează avansurile spre decontare separat de restul plăților în numerar către angajați, deși ele intră în același calcul de plafon zilnic conform art. 3 alin. (4).
- Se fragmentează o factură mare în mai multe încasări succesive pentru a rămâne sub plafon — practică interzisă explicit de lege, indiferent de intervalul de timp dintre tranșe.

## Ce face iConta.eu

Aplicația verifică automat aceste plafoane la nivelul casieriei: motorul de casă calculează, pe baza operațiunilor înregistrate, depășirea plafonului de încasare/plată per persoană juridică (5.000 lei, respectiv 10.000 lei pentru cash and carry) și a plafonului pentru avansuri spre decontare (5.000 lei/persoană/zi), generând avertismente la fiecare operațiune și la închiderea registrului de casă lunar.

[iConta.eu](/)
