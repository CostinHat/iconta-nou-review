---
title: "Contabilitate HoReCa 2026: ce costuri se pot deduce la un restaurant"
description: "Condițiile generale de deductibilitate a cheltuielilor la impozitul pe profit, aplicate specificului unui restaurant, și tratamentul separat al bacșișului."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Contabilitate HoReCa 2026: ce costuri se pot deduce la un restaurant

Un restaurant nu are un regim special de deductibilitate a cheltuielilor — se aplică regulile generale ale Codului fiscal, cu câteva plafoane specifice (cheltuieli sociale, protocol) și cu o particularitate reală a domeniului: bacșișul, care are propriul regim fiscal, separat de restul veniturilor și cheltuielilor.

## Temeiul legal

::: ghid-temei
„cheltuielile sociale, în limita unei cote de până la 5%, aplicată asupra valorii cheltuielilor cu salariile personalului, potrivit Codului muncii."
— Legea 227/2015, art. 25 alin. (3) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce e specific unui restaurant, în plus față de regulile generale de deductibilitate:

- **Cheltuielile cu materia primă și mărfurile** (alimente, băuturi) sunt deductibile în regulile generale, cu condiția documentelor justificative complete — facturi, recepții, NIR-uri corecte.
- **Cheltuielile sociale** (mese calde pentru personal, dacă sunt tratate ca atare, facilități pentru angajați) intră sub plafonul de 5% din cheltuielile anuale cu salariile, ca la orice altă firmă.
- **Bacșișul** are un regim fiscal complet separat de restul activității: potrivit Legii 376/2022 și art. 115 din Codul fiscal, bacșișul evidențiat distinct pe bonul fiscal **nu intră în baza de TVA**, **nu e supus CAS/CASS** și e impozitat cu **10%** (impozit pe venit din alte surse), reținut la sursă la distribuire către angajați, cu plată până pe 25 a lunii următoare și raportare informativă prin D205.
- Deducerea cheltuielilor cu protocolul (mese oferite partenerilor de afaceri, evenimente) urmează regulile generale de plafonare din Codul fiscal, distincte de cele pentru cheltuieli sociale.

## Ce se greșește în practică

- Se tratează bacșișul ca parte din venitul din vânzări al restaurantului, inclus în baza de TVA — bacșișul evidențiat distinct e explicit în afara sferei TVA, iar includerea lui greșită denaturează atât TVA colectată, cât și baza de calcul a altor obligații.
- Se deduc integral, fără plafonare, cheltuielile sociale legate de personal (mese, facilități), ignorând limita de 5% din cheltuielile anuale cu salariile.
- Se aplică regimul salarial obișnuit (CAS/CASS, impozit pe venit din salarii) asupra bacșișului distribuit angajaților, deși legea prevede un regim distinct — impozit pe venit din alte surse, de 10%, fără contribuții sociale.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are un motor real pentru tratamentul fiscal al bacșișului (`core/bacsis.py`), care separă corect încasarea de la client (461=462, cu încasare 5121/5311=461) de impozitarea la distribuire (10%, cont 446, plată netă 462=5121/5311), fără TVA și fără CAS/CASS, conform Legii 376/2022 și art. 115 din Codul fiscal. Pentru restul cheltuielilor unui restaurant (materie primă, cheltuieli sociale, protocol), aplicația oferă evidența contabilă generală, dar nu calculează automat plafonul de 5% pentru cheltuielile sociale — verificarea acestuia rămâne manuală.

[iConta.eu](/)
