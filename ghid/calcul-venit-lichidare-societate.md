---
title: Cum se calculează venitul din lichidarea unei societăți?
description: Câștigul impozabil la partaj este rezervele plus profiturile (capitalul social restituit e neimpozabil), iar legea cere o cotă fixă de 10% pentru asociați persoane fizice — nu cota dividendelor (art.97 alin.5 Cod fiscal); iConta.eu aplică cota corectă de 10%, dar nu distinge încă asociatul persoană fizică de cel juridic.
published: 2026-09-22
modified: 2026-09-23
poarta: v1
---

# Cum se calculează venitul din lichidarea unei societăți?

Venitul din lichidare este, din punct de vedere fiscal, o categorie separată de dividende — cu propria definiție, propriul articol din Codul fiscal și propria cotă. Confuzia dintre cele două este exact locul unde apar cele mai costisitoare greșeli, inclusiv în calculul automatizat.

## Temeiul legal

::: ghid-temei
**Cod fiscal 227/2015, art.7 pct.11 lit.c):**
"dividend - o distribuire în bani sau în natură, efectuată de o persoană juridică unui participant, drept consecință a deținerii unor titluri de participare la acea persoană juridică, exceptând următoarele: ... c) o distribuire în bani sau în natură, efectuată în legătură cu lichidarea unei persoane juridice;"

**Cod fiscal 227/2015, art.91 lit.a) și lit.e):**
"Veniturile din investiții cuprind: a) venituri din dividende; ... e) venituri din lichidarea unei persoane juridice."

**Cod fiscal 227/2015, art.97 alin.(5):**
"Venitul impozabil obținut din lichidarea unei persoane juridice de către acționari/asociați persoane fizice sau din reducerea capitalului social, potrivit legii, care nu reprezintă distribuții în bani sau în natură ca urmare a restituirii cotei-părți din aporturi se impun cu o cotă de 10%, impozitul fiind final. Obligația calculării, reținerii și plății impozitului revine persoanei juridice. Impozitul calculat și reținut la sursă în cazul lichidării persoanei juridice se plătește până la data depunerii situației financiare finale la oficiul registrului comerțului, întocmită de lichidatori, respectiv până la data de 25 a lunii următoare celei în care a fost distribuit venitul reprezentând reducerea capitalului social."

**Cod fiscal 227/2015, art.97 alin.(7):**
"Veniturile sub formă de dividende, inclusiv câștigul obținut ca urmare a deținerii de titluri de participare... se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor..."

**Cod fiscal 227/2015, art.23 lit.j):**
"veniturile din lichidarea unei alte persoane juridice române sau unei persoane juridice străine situate într-un stat cu care România are încheiată o convenție de evitare a dublei impuneri, dacă la data începerii operațiunii de lichidare, potrivit legii, contribuabilul deține pe o perioadă neîntreruptă de un an minimum 10% din capitalul social al persoanei juridice supuse operațiunii de lichidare;"
:::

## Baza impozabilă și cota corectă

La partajul final, nu tot ce se distribuie asociaților e impozabil. Capitalul social restituit este **neimpozabil** — e doar restituirea aportului inițial al asociaților. Ce rămâne impozabil este ce depășește aportul: rezervele și profiturile distribuite (rezultatul reportat, rezultatul lichidării).

Pentru **asociați persoane fizice**, legea stabilește o cotă proprie, fixă, de **10%**, la art.97 alin.(5) — o normă complet separată de cota dividendelor obișnuite (art.97 alin.7). Cele două sunt distincte încă de la definiție: art.7 pct.11 lit.c) exclude explicit din categoria "dividend" orice distribuire legată de lichidare, iar art.91 le listează ca litere separate (dividende la lit.a, venituri din lichidare la lit.e). Impozitul e final, calculat și reținut de firmă, și se plătește până la data depunerii situației financiare finale la Registrul Comerțului.

::: ghid-exemplu
Un SRL cu capital social 10.000 lei, rezerve 5.000 lei și profit reportat 15.000 lei, la partajul final către un asociat persoană fizică unic:

- Capital social restituit: 10.000 lei — neimpozabil.
- Câștig impozabil: 5.000 + 15.000 = 20.000 lei.
- Impozit corect, conform art.97 alin.(5): 20.000 × 10% = **2.000 lei**.
- Sumă netă cuvenită asociatului: 10.000 + 20.000 − 2.000 = **28.000 lei**.
:::

Pentru un **asociat persoană juridică**, regimul poate fi complet diferit: dacă acesta deține minimum 10% din capitalul social al firmei lichidate, neîntrerupt, de peste un an, câștigul din lichidare este **neimpozabil** la asociatul-PJ, conform art.23 lit.j). Legea nu tratează la fel asociații persoane fizice și cei persoane juridice.

## Ce se greșește în practică

- Se calculează impozitul pe câștigul din lichidare cu cota dividendelor obișnuite, considerând că "e tot un fel de dividend" — legea le tratează explicit ca venituri separate, cu cote diferite.
- Se include capitalul social restituit în baza impozabilă, deși el este neimpozabil prin definiție.
- Se aplică aceeași cotă indiferent de tipul asociatului, ignorând că un asociat persoană juridică poate fi complet neimpozabil, dacă îndeplinește condiția de deținere din art.23 lit.j).
- Se plătește impozitul reținut la termenul general de 25 a lunii, deși termenul legal pentru lichidare e legat de data depunerii situației financiare finale.

## Ce face iConta.eu

Funcția de partaj din motorul de lichidare al aplicației calculează corect baza impozabilă — câștigul impozabil este rezervele plus profiturile, capitalul social fiind exclus. Din 23.09.2026, aplicația aplică și **cota corectă: 10% fix (CF art.97 alin.5)** pentru câștigul din lichidare la asociați persoane fizice — distinctă de cota dividendelor (art.97 alin.7, 16% din 2026), care nu se mai folosește aici. Interfața afișează explicit cota folosită la fiecare notă de partaj generată.

Rămâne o limitare: aplicația nu distinge tipul asociatului (persoană fizică sau juridică) — cota de 10% se aplică uniform. Pentru asociați-PJ care îndeplinesc condiția de deținere din art.23 lit.j), regimul de neimpozitare a câștigului din lichidare nu este luat în calcul.

Pentru un asociat persoană juridică ce ar putea beneficia de neimpozitare (art.23 lit.j), nota de partaj generată trebuie verificată și, dacă e cazul, ajustată. Pentru asociați persoane fizice, cota de 10% aplicată automat e cea corectă.

[iConta.eu](/)
