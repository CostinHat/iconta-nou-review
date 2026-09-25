---
title: "Cum se taxează telefonul de serviciu folosit și personal?"
description: "Regimul fiscal al convorbirilor telefonice de serviciu folosite și în scop personal: când costul e neimpozabil și când devine avantaj în natură pentru salariat."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se taxează telefonul de serviciu folosit și personal?

Un telefon de serviciu folosit strict pentru sarcini de serviciu nu generează niciun avantaj impozabil pentru salariat. Problema apare când telefonul e folosit și în scop personal — legea cere angajatorului să separe cele două componente, nu să le trateze automat ca fiind integral neimpozabile sau integral impozabile.

## Temeiul legal

::: ghid-temei
„(7) Nu sunt considerate avantaje: [...] c) costul abonamentelor telefonice și al convorbirilor telefonice efectuate, precum și utilizarea autoturismului de serviciu pentru îndeplinirea sarcinilor de serviciu; [...]
(8) Angajatorul stabilește partea corespunzătoare din convorbirile telefonice reprezentând folosința în scop personal, care reprezintă avantaj impozabil, în condițiile art. 76 alin. (3) din Codul fiscal, și se va impozita prin cumulare cu veniturile salariale ale lunii în care salariatul primește acest avantaj. În acest scop angajatorul stabilește limita convorbirilor telefonice aferente sarcinilor de serviciu pentru fiecare post telefonic, urmând ca ceea ce depășește această limită să fie considerat avantaj în natură, în situația în care salariatului în cauză nu i s-a imputat costul convorbirilor respective."
— HG 1/2016, pct. 12 alin. (7) lit. c) și alin. (8) (norme de aplicare a art. 76 din Codul fiscal) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

Din text rezultă un mecanism în trei pași, în sarcina angajatorului:

- **Costul convorbirilor pentru sarcini de serviciu nu e avantaj** — atâta timp cât abonamentul și convorbirile sunt folosite pentru îndeplinirea atribuțiilor de serviciu, nu se impozitează nimic.
- **Angajatorul trebuie să stabilească o limită** a convorbirilor considerate de serviciu, pentru fiecare post telefonic — nu există o limită legală fixă, ci una internă, documentată de firmă.
- **Ce depășește limita e avantaj în natură**, dar numai dacă salariatul nu a suportat el însuși (nu i s-a imputat) costul depășirii — dacă angajatul plătește contravaloarea convorbirilor personale, nu mai apare avantaj impozabil.
- **Avantajul se cumulează cu salariul lunii** în care e constatat și se impozitează ca venit din salarii, potrivit art. 76 alin. (3) din Codul fiscal.

## Ce se greșește în practică

- Se consideră întregul abonament de telefon mobil ca fiind neimpozabil, fără să existe vreo limită stabilită de angajator pentru convorbirile de serviciu — condiția din alin. (8) presupune existența unei limite documentate, nu doar afirmația că telefonul e „de firmă".
- Se calculează avantajul în natură fără să se verifice întâi dacă salariatul a suportat costul convorbirilor personale — imputarea către salariat elimină avantajul impozabil.
- Se confundă regimul telefonului cu cel al vehiculului cu folosință mixtă (art. 25 alin. (3) lit. l) din Codul fiscal) — cele două au reguli de evaluare diferite în aceleași norme (pct. 12), nu se aplică metoda proporției kilometrilor la telefon.
- Se omite impozitarea completă: chiar dacă avantajul e mic, el trebuie cumulat cu salariul lunii respective și supus contribuțiilor/impozitului pe venit ca orice alt avantaj în natură.

## Ce face iConta.eu

La data acestui ghid, iConta.eu gestionează în `core/beneficii_api.py` beneficii tipizate acordate salariaților — cadouri, vouchere de vacanță — cu praguri și tratament fiscal specific fiecărui tip. Nu există în cod un tip de beneficiu dedicat convorbirilor telefonice personale și nicio funcție care să calculeze automat depășirea limitei de convorbiri de serviciu stabilite intern de angajator. Stabilirea limitei per post telefonic și calculul avantajului rămân, la acest moment, o operațiune manuală a angajatorului/contabilului, introdusă apoi ca venit asimilat salariului, dacă e cazul.

[iConta.eu](/)
