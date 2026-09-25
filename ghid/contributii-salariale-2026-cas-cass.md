---
title: "Contribuții salariale 2026: CAS, CASS și impozit pe venit"
description: "Cotele de CAS, CASS și impozit pe venit reținute din salariul brut în 2026, potrivit Codului fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Contribuții salariale 2026: CAS, CASS și impozit pe venit

Din salariul brut al unui angajat, angajatorul reține trei sume distincte, fiecare cu cota și baza ei proprie: contribuția de asigurări sociale (CAS), contribuția de asigurări sociale de sănătate (CASS) și impozitul pe venitul din salarii. Cele trei se calculează în cascadă, nu în paralel — ordinea contează.

## Temeiul legal

::: ghid-temei
„Cotele de contribuții de asigurări sociale sunt următoarele: a) 25% datorată de către persoanele fizice care au calitatea de angajați sau pentru care există obligația plății contribuției de asigurări sociale, potrivit prezentei legi [...]"
— Legea nr. 227/2015, art. 138 lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Cota de contribuție de asigurări sociale de sănătate este de 10% și se datorează de către persoanele fizice care au calitatea de angajați sau pentru care există obligația plății contribuției de asigurări sociale de sănătate, potrivit prezentei legi."
— Legea nr. 227/2015, art. 156 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„[...] la locul unde se află funcția de bază, prin aplicarea cotei de 10% asupra bazei de calcul determinată ca diferență între venitul net din salarii calculat prin deducerea din venitul brut a contribuțiilor sociale obligatorii aferente unei luni [...] și [...] deducerea personală acordată pentru luna respectivă [...]"
— Legea nr. 227/2015, art. 78 alin. (2) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ordinea de calcul, pornind de la salariul brut:

1. **CAS = 25%** din salariul brut (baza fiind, în cazul simplu, chiar brutul lunar).
2. **CASS = 10%** din salariul brut, calculat separat, nu din baza rămasă după CAS.
3. **Impozitul pe venit = 10%**, aplicat nu pe brut, ci pe **venitul net** — adică brutul din care s-au scăzut deja CAS, CASS și deducerea personală (și, după caz, cotizația sindicală sau contribuțiile la pensii facultative/ocupaționale, în limitele legale).

## Ce se greșește în practică

- Se calculează impozitul pe venit direct din salariul brut, fără a scădea întâi CAS și CASS — ordinea din art. 78 alin. (2) lit. a) e obligatorie, nu opțională.
- Se aplică CAS și CASS pe baze diferite (de exemplu CASS pe venitul rămas după CAS), deși ambele contribuții se calculează independent, din același brut.
- Se omite deducerea personală la calculul impozitului, deși aceasta reduce baza de impozitare înainte de aplicarea cotei de 10%.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează, în modulul de salarizare, CAS, CASS și impozitul pe venit pentru fiecare salariat, pornind de la salariul brut din contract și aplicând cotele din registrul de cote al aplicației (25% CAS, 10% CASS, 10% impozit), inclusiv deducerea personală și regulile speciale pentru salariul minim sau part-time. Rezultatele alimentează atât statul de plată, cât și generarea **D112**.

[iConta.eu](/)
