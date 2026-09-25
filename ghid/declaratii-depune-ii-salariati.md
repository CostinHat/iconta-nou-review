---
title: "Ce declarații depune o II care are salariați?"
description: "Obligațiile declarative ale unei întreprinderi individuale care are și angajați: D112 pentru salariați și, separat, Declarația unică D212 pentru venitul propriu al titularului."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce declarații depune o II care are salariați?

O întreprindere individuală (II) cu angajați se află, fiscal, în două poziții simultan: e **angajator** pentru salariații ei, cu obligațiile de reținere la sursă ale oricărei firme, și rămâne, separat, **persoană fizică autorizată să obțină venit din activitate independentă**, cu propria obligație de declarare a venitului. Cele două fluxuri nu se contopesc într-o singură declarație.

## Temeiul legal

::: ghid-temei
„Beneficiarii de venituri din salarii și asimilate salariilor datorează un impozit lunar, final, care se calculează și se reține la sursă de către plătitorii de venituri [...]"
— Codul fiscal (Legea 227/2015), art. 78 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Persoanele fizice care în anul fiscal pentru care se depune Declarația unică privind impozitul pe venit și contribuțiile sociale datorate de personale fizice [...] au realizat venituri din activitățile prevăzute la art. 137 alin. (1) lit. b) și b^1), din una sau mai multe surse și/sau categorii de venituri, a căror valoare anuală cumulată este cel puțin egală cu 12 salarii minime brute pe țară, datorează contribuția de asigurări sociale la o bază de calcul stabilită potrivit alin. (2)."
— Codul fiscal, art. 148 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cele două seturi de obligații, separate:

- **Ca angajator**, II reține și declară lunar, prin **D112**, impozitul pe salarii (art. 78 CF) și contribuțiile sociale (CAS, CASS, CAM) ale fiecărui salariat — exact ca orice altă firmă, indiferent de forma juridică.
- **Ca titular al activității independente**, II declară anual, prin **Declarația unică (D212)**, venitul net obținut din propria activitate. Dacă venitul anual (cumulat cu eventuale alte venituri din aceeași categorie) atinge pragul de 12 salarii minime brute pe țară, se datorează și CAS (art. 148 CF) — regula echivalentă există și pentru CASS.
- Cele două declarații au **termene și mecanisme diferite**: D112 e lunară, legată de statul de plată al fiecărei luni; D212 e anuală, legată de venitul net din registrul de încasări și plăți al II.
- Numărul de angajați nu schimbă regimul fiscal al II pe venitul propriu (sistem real sau normă de venit) — angajarea de personal e independentă de modul în care se determină venitul net al titularului.

## Ce se greșește în practică

- Se crede că D212 „acoperă" și obligațiile salariale, sau invers — sunt fluxuri complet separate, cu surse de date diferite (statul de plată vs. registrul de încasări și plăți).
- Se omite depunerea D112 pe motiv că II „nu e o firmă adevărată" — obligația de reținere la sursă pentru salariați se aplică indiferent de forma juridică a angajatorului.
- Se aplică pragul de 12 salarii minime pentru CAS/CASS al titularului fără să se cumuleze toate veniturile din aceeași categorie realizate în acel an, dacă titularul are mai multe surse.

## Ce face iConta.eu

Cele două fluxuri sunt implementate ca funcționalități separate și reale în aplicație, exact pe granița descrisă mai sus: **D112** (`core/d112.py`) se construiește automat din statul de plată (`core/stat_plata_api.py`, alimentat din fișa fiecărui salariat — `core/salariati_api.py`), cu contribuțiile și impozitul pe salarii pe fiecare asigurat. **Motorul D212** (`core/d212_engine.py`) calculează separat, în sistem real, venitul net și contribuțiile CAS/CASS pe plafoanele de salarii minime, pornind din registrul de încasări și plăți al II (`core/rip_api.py`). Aplicația nu unește cele două module într-un singur ecran sau declarație — fiecare urmează sursa lui de date, așa cum cere și legea.

[iConta.eu](/)
