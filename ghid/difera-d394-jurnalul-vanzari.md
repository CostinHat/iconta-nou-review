---
title: "De ce diferă D394 de jurnalul de vânzări?"
description: "D394 nu e un rezumat al jurnalului de vânzări: conține doar operațiunile taxabile în România, raportabile B2B conform OPANAF 2194/2025, în timp ce jurnalul de vânzări cuprinde toate vânzările firmei."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# De ce diferă D394 de jurnalul de vânzări?

Jurnalul de vânzări conține toate vânzările firmei, indiferent de client sau destinație; D394 raportează doar un subset — operațiunile taxabile în România, cu partenerii și tratamentul TVA prevăzute explicit de OPANAF 2194/2025.

## Temeiul legal

::: ghid-temei
„Persoanele impozabile înregistrate în scopuri de TVA în România sunt obligate să declare livrările de bunuri, prestările de servicii şi achiziţiile de bunuri şi servicii realizate pe teritoriul României către/de la orice persoană, aşa cum este definită la art. 266 alin. (1) pct. 24 din Legea nr. 227/2015 privind Codul fiscal, cu modificările şi completările ulterioare."
— OPANAF 3769/2015, art. 1 (sursă: anaf_surse/opanaf_3769_2015_d394_baza.txt)

„De asemenea, în declaraţie se înscrie valoarea totală a facturilor simplificate şi a bonurilor fiscale care îndeplinesc condiţiile unei facturi simplificate conform prevederilor art. 319 alin. (12), (13) şi (21) din Codul fiscal, dacă au înscris codul de înregistrare în scopuri de TVA al beneficiarului."
— OPANAF 2194/2025, Anexa 2 (sursă: anaf_surse/opanaf_2194_2025_d394.txt)
:::

Principalele surse de diferență între jurnalul de vânzări (evidența completă) și D394 (declarația transmisă la ANAF):

- **Granularitate diferită.** Jurnalul de vânzări listează fiecare factură individual. D394 agregă multe operațiuni — de exemplu, bonurile fiscale/facturile simplificate apar ca valoare totală pe cotă, nu ca linii separate.
- **Vânzări către persoane fizice, fără factură cu CUI.** Aceste operațiuni apar în jurnalul de vânzări ca venit, dar în D394 intră doar dacă sunt emise ca bon fiscal/factură simplificată care îndeplinește condițiile legale — și oricum agregat, nu individual.
- **Livrări intracomunitare și exporturi** apar în ambele, dar în D394 sunt clasificate diferit (tip L/LS, la cotă 0), în timp ce jurnalul de vânzări le înregistrează contabil pe baza documentului.
- **Operațiuni scutite fără drept de deducere** sau alte categorii care nu se încadrează în definiția din OPANAF 2194/2025 pot lipsi din perimetrul D394, deși există în jurnalul de vânzări ca venit contabil.

## Ce se greșește în practică

- Se așteaptă ca totalul veniturilor din jurnalul de vânzări să coincidă cu baza impozabilă totală din D394 — nu ar trebui, pentru că D394 nu e un rezumat al jurnalului, ci o selecție cu reguli proprii de includere.
- Se tratează orice diferență ca semn de eroare, fără să se verifice întâi dacă operațiunea lipsă e de tipul celor excluse legal (de exemplu, o vânzare fără factură cu partener identificat, raportată doar agregat).
- Se compară cele două surse linie cu linie, ignorând că D394 grupează unele operațiuni (bonuri fiscale, facturi simplificate) pe total, nu individual.

## Ce face iConta.eu

Generatorul D394 (`core/d394.py`) citește facturile din aceeași tabelă unică (`facturi` + `factura_linii`) folosită și pentru evidența contabilă a firmei, cu filtre proprii de tip document (exclude proforme/avize) și de status (exclude ciorne, facturi anulate/stornate). Diferențele față de jurnalul de vânzări complet apar tocmai din aceste filtre și din regulile de agregare specifice D394 descrise mai sus, nu dintr-o eroare de generare.

Aplicația are o a doua cale de calcul, independentă (`core/d394_reconciliere.py`), care recalculează totalurile pe cotă direct din liniile brute ale facturilor și oprește generarea dacă diferă de rezultatul generatorului principal — dar acest gard confirmă coerența internă a D394, nu o compară cu jurnalul de vânzări în ansamblu. **iConta.eu nu are o funcție dedicată care să compare automat D394 cu jurnalul de vânzări** — o eventuală divergență trebuie interpretată manual, pe baza regulilor de scop explicate mai sus.

[iConta.eu](/)
