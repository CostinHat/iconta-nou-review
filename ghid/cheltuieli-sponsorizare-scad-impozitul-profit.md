---
title: 'Cheltuieli de sponsorizare: cum se scad din impozitul pe profit'
description: Sponsorizarea nu reduce profitul impozabil, ci se scade direct din impozitul pe profit datorat, ca și credit fiscal — dar numai până la minimul dintre 0,75% din cifra de afaceri și 20% din impozitul pe profit; peste plafon, suma rămâne cheltuială fără efect fiscal.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cheltuieli de sponsorizare: cum se scad din impozitul pe profit

O greșeală frecventă e să tratați sponsorizarea ca pe orice altă cheltuială — dedusă din profitul impozabil, reducând indirect impozitul cu doar 16% din valoarea ei. Legea îi dă însă un tratament mai bun, dar și mai strict: sponsorizarea nu se deduce din bază, ci se scade **direct din impozitul pe profit datorat**, ca și credit fiscal, în limita unui plafon dublu.

## Temeiul legal

::: ghid-temei
„i) cheltuielile de sponsorizare și/sau mecenat, acordate potrivit legii; contribuabilii care efectuează sponsorizări și/sau acte de mecenat, potrivit prevederilor Legii nr. 32/1994 privind sponsorizarea..., scad sumele aferente din impozitul pe profit datorat la nivelul valorii minime dintre următoarele:
1. valoarea calculată prin aplicarea a 0,75% la cifra de afaceri; pentru situațiile în care reglementările contabile aplicabile nu definesc indicatorul cifra de afaceri, această limită se determină potrivit normelor;
2. valoarea reprezentând 20% din impozitul pe profit datorat. În cazul sponsorizărilor efectuate către entități persoane juridice fără scop lucrativ, inclusiv unități de cult, sumele aferente acestora se scad din impozitul pe profit datorat, în limitele prevăzute de prezenta literă, doar dacă beneficiarul sponsorizării este înscris, la data încheierii contractului, în Registrul entităților/unităților de cult pentru care se acordă deduceri fiscale, potrivit alin. (4^1).”

— *Codul fiscal, art. 25 alin. (4) lit. i), forma actuală.*
:::

## Cei doi pași care nu trebuie săriți

1. **Nu scădeți suma sponsorizată direct din impozit.** Calculați întâi plafonul — minimul dintre 0,75% din cifra de afaceri și 20% din impozitul pe profit datorat. Doar suma din limita plafonului se scade efectiv din impozit; ce depășește plafonul rămâne cheltuială fără niciun efect asupra impozitului pe profit din acel an.
2. **Verificați Registrul ANAF pentru beneficiar, dacă e o entitate nonprofit/cult.** Beneficiarul trebuie să fie înscris în Registrul entităților/unităților de cult pentru care se acordă deduceri fiscale, la data încheierii contractului — nu la data plății. Dacă lipsește această înscriere, creditul e 0 pentru acea sponsorizare, indiferent cât de mult din plafon ar fi acoperit.

::: ghid-exemplu
Firmă cu cifra de afaceri 1.500.000 lei, impozit pe profit datorat 40.000 lei, sponsorizare efectivă 12.000 lei către o entitate nonprofit înscrisă în Registru. Plafon = min(0,75% × 1.500.000; 20% × 40.000) = min(11.250; 8.000) = 8.000 lei. Creditul scăzut din impozit e 8.000 lei; restul de 4.000 lei rămâne cheltuială fără efect asupra impozitului pe profit al anului respectiv, dar spațiul de 0 lei rămas neconsumat din plafon (8.000 − 8.000) înseamnă că nu mai există nimic de redirecționat prin D177.
:::

## Ce se greșește în practică

- Se scade suma sponsorizată integral din impozit, fără a o compara întâi cu plafonul dublu.
- Se ignoră faptul că plafonul e minimul, nu maximul, dintre cele două valori — dacă cifra de afaceri e mare, dar impozitul pe profit e mic, impozitul mic este cel care limitează.
- Se omite verificarea Registrului ANAF la data încheierii contractului, presupunând că orice ONG e automat eligibil.
- Se aplică 0,75% pentru sponsorizări acordate înainte de 03.02.2022, când procentul legal era 0,5%.

## Ce face iConta.eu

`core/sponsorizari.py`, funcția `credit_sponsorizare(cifra_afaceri, impozit_profit, sponsorizari_efectuate, tip_impozit="profit", beneficiar_in_registru=True, la_data=None)`, implementează ambele verificări: respinge creditul (0) dacă `beneficiar_in_registru=False`, altfel calculează `credit = min(sponsorizari_efectuate, plafon_credit(cifra_afaceri, impozit_profit))`. Spațiul neconsumat din plafon, `redirectionabil_d177 = plafon - credit`, e disponibil pentru redirecționare separată prin D177, până la termenul de depunere a D101.

[iConta.eu](/)
