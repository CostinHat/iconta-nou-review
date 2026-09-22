---
title: Cum arată ultima declarație a unui PFA care se radiază?
description: Ultima D212 a unui PFA radiat acoperă venitul net realizat efectiv până la finalul activității, cu praguri CAS/CASS anuale neprorate, iar declarația se depune pentru anul fiscal în care a avut loc radierea, nu doar pentru lunile de dinainte de ea.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum arată ultima declarație a unui PFA care se radiază?

Ultima declarație unică (D212) a unui PFA care se radiază nu diferă structural de o declarație obișnuită — conține aceleași capitole (venit brut, cheltuieli deductibile, CAS, CASS, impozit), calculate pe venitul net efectiv realizat în anul fiscal al radierii. Ce se schimbă e doar orizontul de timp: activitatea a încetat la un moment dat în cursul anului, dar declarația tot acoperă întregul an fiscal.

## Temeiul legal

::: ghid-temei
**Art. 151 alin.(2):** "Prevederile alin. (1), precum și cele ale art. 148 sunt aplicabile și în cazul contribuabililor care în cursul anului fiscal încep o activitate independentă și/sau încep să realizeze venituri din drepturi de proprietate intelectuală, precum și în cazul celor care intră în suspendare temporară a activității ... ori își încetează activitatea."

**Art. 68 alin.(1):** "Venitul net anual din activități independente se determină în sistem real, pe baza datelor din contabilitate, ca diferență între venitul brut și cheltuielile deductibile efectuate în scopul realizării de venituri, cu excepția situațiilor în care sunt aplicabile prevederile art. 68^1, 68^3 și 69."
:::

## Ce trebuie verificat la ultima declarație

- **Venitul net cumulat pe tot anul fiscal**, nu doar pe lunile scurse până la data radierii — orice încasare validă legată de activitate, din anul respectiv, intră în calcul.
- **Pragurile CAS (12/24 salarii minime) și CASS (obligatorie peste orice venit net pozitiv, cu bază minimă de 6 salarii minime)** se aplică la valoarea lor anuală întreagă, fără proratare — radierea în cursul anului nu reduce proporțional pragurile.
- **Cheltuielile deductibile plătite până la data efectivă a radierii**, inclusiv eventuale cheltuieli finale legate de închiderea activității, dacă îndeplinesc condițiile de justificare de la art. 68 alin. (4).
- **Anul de venit trebuie să fie unul acceptat de motorul de calcul** (2025 sau 2026) — pentru radieri din alți ani, plafoanele trebuie verificate separat la sursele oficiale.

## Ce se greșește în practică

- Se depune declarația considerând doar veniturile din lunile de dinainte de radiere, omițând încasări ulterioare legate de activitate, dar primite în același an fiscal.
- Se crede că radierea în cursul anului scutește automat de CAS sau CASS, indiferent de nivelul venitului net realizat — nu e cazul dacă venitul net trece pragurile legale.
- Se confundă data radierii de la Registrul Comerțului cu data limită de depunere a declarației unice — termenele de depunere sunt cele generale (an fiscal următor), nu legate direct de data radierii.
- Se omit cheltuielile deductibile plătite chiar în perioada de închidere a activității, deși pot fi justificate și deductibile.

## Ce face iConta.eu

Fișa D212 (`core/rip_api.py: fisa_d212`) însumează toate încasările și plățile validate din anul fiscal declarat, indiferent de data exactă a radierii în cursul anului — nu există o logică separată pentru "perioada de dinainte de radiere" versus restul anului. Calculul CAS și CASS (`core/d212_engine.py`) aplică pragurile anuale întregi, conform art. 151 alin. (2). Motorul acceptă generarea declarației doar pentru venituri din 2025 sau 2026; pentru un an anterior, plafoanele trebuie verificate manual la surse oficiale, iar generatorul XML (`core/d212.py`) oricum nu acceptă un an de raportare sub 2025.

[iConta.eu](/)
