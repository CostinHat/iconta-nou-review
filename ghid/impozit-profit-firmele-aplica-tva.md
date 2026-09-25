---
title: "Impozit pe profit la firmele care aplică TVA normal"
description: "Cum se calculează impozitul pe profit pentru o firmă înregistrată în scopuri de TVA cu regimul normal (nu TVA la încasare) și de ce regimul de TVA nu schimbă baza de calcul a impozitului pe profit."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Impozit pe profit la firmele care aplică TVA normal

Regimul de TVA (normal, adică exigibilitate la facturare, sau la încasare) nu influențează modul de calcul al impozitului pe profit. Rezultatul fiscal se determină întotdeauna pe baza veniturilor și cheltuielilor înregistrate contabil — iar TVA-ul colectat și deductibil nu este, oricum, nici venit, nici cheltuială, ci o taxă evidențiată prin conturi de TVA (4427/4426), neutră față de rezultatul contabil și fiscal.

## Temeiul legal

::: ghid-temei
„(1) Rezultatul fiscal se calculează ca diferență între veniturile și cheltuielile înregistrate conform reglementărilor contabile aplicabile, din care se scad veniturile neimpozabile și deducerile fiscale și la care se adaugă cheltuielile nedeductibile. La stabilirea rezultatului fiscal se iau în calcul și elemente similare veniturilor și cheltuielilor, potrivit normelor metodologice, precum și pierderile fiscale care se recuperează în conformitate cu prevederile art. 31. Rezultatul fiscal pozitiv este profit impozabil, iar rezultatul fiscal negativ este pierdere fiscală.
(2) Rezultatul fiscal se calculează trimestrial/anual, cumulat de la începutul anului fiscal."
— Legea nr. 227/2015 (Codul fiscal), art. 19 alin. (1), (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă de aici pentru o firmă cu TVA în regim normal:

- Baza de calcul a impozitului pe profit este definită exclusiv prin raportare la veniturile și cheltuielile contabile, nu la fluxurile de TVA. Facturile emise/primite intră în rezultatul fiscal la valoarea fără TVA, indiferent dacă firma aplică TVA la exigibilitate normală (la livrare/prestare) sau TVA la încasare.
- Sistemul TVA la încasare (art. 282 alin. (3) și urm. din Codul fiscal) este un mecanism separat, care amână doar **exigibilitatea taxei pe valoarea adăugată** — nu are efect asupra momentului în care venitul sau cheltuiala intră în calculul impozitului pe profit, care rămâne guvernat de principiul contabilității de angajament.
- Prin urmare, o firmă cu TVA normal (fără opțiune pentru TVA la încasare) nu are, doar din acest motiv, vreo particularitate în calculul impozitului pe profit față de o firmă cu TVA la încasare — regulile de la art. 19 și următoarele din titlul II se aplică identic.

## Ce se greșește în practică

- Se crede greșit că firmele cu TVA la încasare pot amâna și recunoașterea venitului impozabil la calculul profitului până la încasarea facturii — venitul contabil (și fiscal) se recunoaște la livrare/prestare, indiferent de regimul de TVA ales.
- Se confundă „TVA normal" (exigibilitate la facturare) cu un regim fiscal distinct la impozitul pe profit, deși cele două impozite (TVA și impozit pe profit) au reguli complet independente de recunoaștere.
- Se omite verificarea separată a condițiilor de eligibilitate pentru impozitul micro (art. 47), presupunându-se că statutul de plătitor de TVA „normal" exclude sau condiționează cumva accesul la regimul micro — cele două nu sunt legate.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează rezultatul fiscal pe baza înregistrărilor contabile ale firmei, prin modulele de impozit pe profit (`core/d101.py`, `core/d101_reconciliere.py`) sau de impozit micro (`core/d100.py`), în funcție de `regim_fiscal` setat în profilul firmei. Regimul de TVA (`platitor_tva`, `tip_decont`) este o setare separată, folosită de motorul fiscal doar pentru a determina declarațiile de TVA datorate (D300, D390 etc., via `core/vector_fiscal_api.py`), nu pentru a modifica baza de calcul a impozitului pe profit sau a impozitului micro.

[iConta.eu](/)
