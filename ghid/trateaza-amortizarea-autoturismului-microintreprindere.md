---
title: "Cum se tratează amortizarea autoturismului la microîntreprindere?"
description: "De ce amortizarea unui autoturism nu are niciun efect fiscal direct la o microîntreprindere, întrucât impozitul se calculează pe venituri, nu pe rezultatul contabil din care s-ar scădea cheltuiala cu amortizarea."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se tratează amortizarea autoturismului la microîntreprindere?

La impozitul pe profit, amortizarea unui autoturism afectează direct baza impozabilă, prin cheltuiala dedusă lunar. La microîntreprindere însă mecanismul de impozitare e complet diferit — iar această diferență e sursa confuziei celor mai multe întrebări despre amortizarea auto la firmele micro.

## Temeiul legal

::: ghid-temei
„(1) Rezultatul fiscal se calculează ca diferență între veniturile și cheltuielile înregistrate conform reglementărilor contabile aplicabile, din care se scad veniturile neimpozabile și deducerile fiscale și la care se adaugă cheltuielile nedeductibile. [...] Rezultatul fiscal pozitiv este profit impozabil, iar rezultatul fiscal negativ este pierdere fiscală."
— Legea nr. 227/2015 (Codul fiscal), art. 19 alin. (1) — regulă generală, Titlul II, Impozitul pe profit (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Citatul de mai sus descrie mecanismul de la impozitul pe profit — cheltuielile (inclusiv amortizarea) se scad din venituri pentru a obține rezultatul fiscal. La microîntreprinderi însă, Titlul III al aceluiași cod stabilește un mecanism diametral opus:

- Impozitul pe veniturile microîntreprinderilor **se calculează direct pe venituri**, potrivit art. 53, fără a scădea cheltuielile din baza impozabilă — deci amortizarea autoturismului, ca orice altă cheltuială, **nu reduce** impozitul datorat de o microîntreprindere.
- Amortizarea rămâne totuși **obligatorie din punct de vedere contabil** — mijlocul fix trebuie amortizat conform planului de amortizare, indiferent de regimul fiscal, pentru a reflecta corect valoarea rămasă a activului în bilanț.
- Situația se schimbă doar dacă firma iese din regimul micro și devine plătitoare de impozit pe profit — din acel moment, amortizarea fiscală a autoturismului (cu limitările specifice de deductibilitate aplicabile autovehiculelor) începe să conteze direct în calculul impozitului.

## Ce se greșește în practică

- Se așteaptă ca achiziția și amortizarea unui autoturism să reducă impozitul micro, similar mecanismului de la impozitul pe profit — la micro, cumpărarea unui autoturism nu are niciun efect fiscal direct asupra impozitului trimestrial.
- Se omite complet amortizarea contabilă a autoturismului, considerând-o „inutilă" fiscal la micro, deși obligația de amortizare contabilă e independentă de regimul fiscal aplicabil.
- Se aplică regulile de deductibilitate limitată (50%) specifice cheltuielilor cu autoturismele de la impozitul pe profit, deși acestea nu au corespondent la impozitul micro, unde cheltuielile nu se scad din bază.

## Ce face iConta.eu

La data acestui ghid, iConta.eu ține evidența mijloacelor fixe și calculează amortizarea contabilă lunară pe baza duratei normale de funcționare introduse (`core/repo_mijloace_fixe.py`), inclusiv pentru autoturisme. Aplicația **nu diferențiază automat** efectul fiscal al amortizării în funcție de regimul firmei (micro sau profit) — ea calculează amortizarea contabilă identic în ambele cazuri, iar interpretarea fiscală (dacă amortizarea reduce sau nu impozitul datorat) rămâne responsabilitatea contabilului, în funcție de regimul fiscal aplicabil firmei.

[iConta.eu](/)
