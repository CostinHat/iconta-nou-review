---
title: Cum se calculează impozitul pe dividende după impozitul pe profit
description: Impozitul pe profit (16%, pe profitul impozabil) și impozitul pe dividende (16%, reținut la plată din profitul rămas) sunt două taxe separate, cu baze de calcul diferite — nu există o formulă unică sau o compensare automată între ele.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se calculează impozitul pe dividende după impozitul pe profit

Cele două impozite se calculează în etape distincte, pe baze diferite, și nu există o formulă unitară care să le lege matematic — impozitul pe profit reduce profitul disponibil pentru distribuire, dar nu intră ca variabilă în calculul impozitului pe dividende.

## Temeiul legal

::: ghid-temei
**Art. 17 din Codul fiscal**: „Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."

**Art. 97 alin. (7) din Codul fiscal**: „Veniturile sub formă de dividende [...] se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor [...] către acționari/asociați/investitori. Termenul de virare a impozitului este până la data de 25 inclusiv a lunii următoare celei în care se face plata."
:::

## Cele două etape

**1. Impozitul pe profit** se calculează întâi, anual (definitivat prin D101) sau cu plăți anticipate trimestriale, aplicând 16% asupra profitului impozabil (venituri minus cheltuieli deductibile, plus ajustările prevăzute de Titlul II din Codul fiscal). Ce rămâne după scăderea acestui impozit din profitul contabil este profitul net, singurul care poate fi propus spre distribuire ca dividend.

**2. Impozitul pe dividende** se calculează separat, abia când AGA (sau asociatul unic) aprobă distribuirea și firma efectuează plata: 16% din dividendul brut plătit persoanei fizice, reținut la sursă de firmă. Baza acestui al doilea impozit este suma dividendului plătit, nu profitul impozabil folosit la primul calcul — cele două cote de 16% se aplică pe două baze complet diferite, în momente diferite.

Dacă dividendul e aprobat spre distribuire dar nu e plătit până la finalul anului, o regulă separată din art. 97 alin. (7) — neinclusă în citatul de mai sus — stabilește un termen distinct de virare a impozitului pentru acest caz; nu am putut verifica verbatim acest text în cadrul acestei treceri, așa că recomandăm confirmarea lui directă la sursă înainte de publicare.

## Ce se greșește în practică

Confuzia cea mai frecventă: se crede că impozitul pe dividende se calculează pe profitul rămas *după* deducerea impozitului pe profit, ca într-o formulă compusă (de exemplu "16% din profitul net"), când de fapt baza lui e strict suma efectiv distribuită/plătită ca dividend, indiferent cum a fost calculat profitul net. A doua greșeală: se încearcă declararea dividendelor prin D101 — D101 e exclusiv declarația de impozit pe profit; dividendele plătite persoanelor fizice se declară separat, prin D205.

## Ce face iConta.eu

Cele două calcule rulează prin module separate ale aplicației: D101 calculează impozitul pe profit (cota de 16% pe profitul impozabil reconstruit din P1–P53, cu deduceri și ajustări automate). Separat, când o distribuire de dividende e înregistrată și validată pe contul 457, D205 se generează automat, cu cota de 16% (aplicabilă din 2026) preluată dintr-un registru central care ține cont de data distribuirii. Nu există în cod nicio verificare sau reconciliere automată între cele două declarații — D101 nu conține nicio referință la dividende sau la contul 457, iar calculul impozitului pe dividende nu depinde de rezultatul D101. Corectitudinea secvenței (impozit pe profit calculat, apoi profit net distribuit, apoi impozit pe dividende reținut) rămâne responsabilitatea contabilului.

[iConta.eu](/)
