---
title: Cum diagnostichez o balanță care dă impozit pe profit greșit
description: Un impozit pe profit greșit vine aproape mereu dintr-un ajustament omis — cheltuiala nedeductibilă cu impozitul, rezerva legală, plafonul de sponsorizare sau amortizarea introdusă doar parțial. Un ghid de verificare pas cu pas, pe baza avertismentelor pe care le rulează generatorul D101.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum diagnostichez o balanță care dă impozit pe profit greșit

Când impozitul pe profit calculat pe D101 pare greșit, cauza e aproape întotdeauna în balanță, nu în formulă — un ajustament fiscal (cheltuială nedeductibilă, deducere, plafon) a fost omis sau introdus incomplet. Verificați punctele de mai jos, în ordinea în care le validează motorul de calcul.

## Temeiul legal

::: ghid-temei
**Art. 18^1 alin. (16) din Codul fiscal** (introdus de OUG nr. 89/2025, în vigoare de la 01.01.2026): „Pentru anul fiscal 2026/anul fiscal modificat care începe în anul 2026, cota de impozit din cadrul formulei prevăzute la alin. (3) este 0,5%."
:::

## Ce verificați, în ordine

**1. Soldul contului 691 (cheltuiala cu impozitul pe profit).** Dacă e pozitiv și rândul de cheltuieli nedeductibile nu conține și această sumă, impozitul iese subevaluat — cheltuiala cu impozitul pe profit e ea însăși nedeductibilă și trebuie adăugată înapoi la baza impozabilă. Omisiunea asta, măsurată pe un portofoliu real de firme, a redus impozitul declarat cu peste 2.400 lei într-un singur caz, fără niciun alt semn vizibil în balanță.

**2. Rezerva legală.** Dacă a fost introdusă manual, verificați plafonul: minimul dintre 5% din baza de calcul (profit contabil brut + cheltuiala cu impozitul) și 20% din capitalul social minus rezerva deja constituită. O rezervă legală peste plafon reduce artificial profitul impozabil.

**3. Sponsorizarea.** Se aplică două limite simultan, nu una singură: 20% din impozitul pe profit datorat ȘI 0,75% din cifra de afaceri — se ia minimul dintre ele. Dacă balanța arată doar verificarea limitei de 20%, fără cea de 0,75% din cifra de afaceri, deducerea poate fi supraevaluată.

**4. Amortizarea, introdusă o singură dată în loc de două.** Amortizarea fiscală (deducere, reduce baza) și cheltuiala contabilă cu amortizarea (dacă e nedeductibilă/neconformă, se adaugă înapoi) sunt două valori distincte care trebuie introduse separat — o eroare frecventă e introducerea unei singure valori, care anulează efectul celeilalte.

**5. Firme mari — IMCA.** Dacă cifra de afaceri a anului precedent depășește 50.000.000 EUR, verificați dacă s-a calculat și impozitul minim pe cifra de afaceri (IMCA), pe lângă impozitul normal pe profit.

**6. Date de identificare.** Declarația nu se poate genera fără CUI valid (verificat pe cifră de control), denumire, adresă și cod CAEN complet (4 cifre) — o eroare aici oprește generarea, nu produce un impozit greșit, dar merită eliminată din lista de suspecți.

## Ce se greșește în practică

Cea mai frecventă cauză a unui impozit greșit e un ajustament fiscal aplicat parțial: contabilul introduce corect amortizarea fiscală (deducerea), dar omite să adauge înapoi amortizarea contabilă neconformă, sau invers. A doua cauză frecventă: sponsorizarea verificată doar pe limita de 20% din impozit, fără cross-check pe 0,75% din cifra de afaceri.

## Ce face iConta.eu

Generatorul D101 rulează automat mai multe validări la fiecare generare: verifică non-negativitatea rândurilor, subtotalurile „din care" față de componente, plafoanele pe credite fiscale/sponsorizare/reduceri, și emite explicit un avertisment când soldul contului 691 e pozitiv fără ca suma corespunzătoare să apară la cheltuieli nedeductibile. **Important pentru firmele eligibile IMCA în 2026**: motorul de calcul din aplicație aplică în prezent o cotă fixă de 1% în formula IMCA, deși legea prevede explicit 0,5% pentru anul fiscal 2026 (art. 18^1 alin. 16, citat mai sus) — pentru firmele cu cifră de afaceri peste 50 milioane EUR, valoarea IMCA afișată de aplicație poate ieși dublă față de cea legal datorată. Verificați manual acest calcul pentru anul fiscal 2026 până la corectarea acestei discrepanțe.

[iConta.eu](/)
