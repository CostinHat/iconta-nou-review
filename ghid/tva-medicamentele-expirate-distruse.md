---
title: TVA la medicamentele expirate distruse
description: Distrugerea dovedită a medicamentelor expirate scutește de ajustarea TVA dedusă la achiziție, dar deductibilitatea cheltuielii la impozitul pe profit rămâne condiționată de documentarea distrugerii, nu automată.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# TVA la medicamentele expirate distruse

Când medicamentele expirate sunt distruse, întrebarea are două fațete distincte: dacă se ajustează TVA-ul dedus la achiziție și dacă valoarea rămâne cheltuială deductibilă la impozitul pe profit. Regula generală de ajustare a TVA cunoaște o excepție explicită pentru bunurile distruse, dar excepția funcționează doar cu dovadă corespunzătoare, nu automat.

## Temeiul legal

::: ghid-temei
„(1) În condițiile în care regulile privind livrarea către sine sau prestarea către sine nu se aplică, deducerea inițială se ajustează în următoarele cazuri: a) deducerea este mai mare sau mai mică decât cea pe care persoana impozabilă avea dreptul să o opereze; [...]

(2) Nu se ajustează deducerea inițială a taxei în cazul: a) bunurilor distruse, pierdute sau furate, în condițiile în care aceste situații sunt demonstrate sau confirmate în mod corespunzător de persoana impozabilă. [...]"

*(Codul fiscal — Legea nr. 227/2015, art. 304 alin. (1) lit. a) și alin. (2) lit. a))*
:::

## Ce înseamnă „demonstrate sau confirmate în mod corespunzător"

Excepția de la ajustarea TVA nu se aplică prin simpla afirmație că medicamentele au expirat — legea cere ca distrugerea să fie „demonstrată sau confirmată în mod corespunzător". În practică, asta înseamnă documentul care atestă distrugerea efectivă (proces-verbal de distrugere, eventual cu participarea unei firme autorizate pentru deșeuri farmaceutice, dat fiind regimul special al medicamentelor). Fără această dovadă, TVA-ul dedus inițial la achiziția medicamentelor trebuie ajustat, conform regulii generale de la art. 304 alin. (1).

## Deductibilitatea cheltuielii, separat de TVA

Ajustarea de TVA și deductibilitatea cheltuielii cu medicamentele scoase din gestiune sunt două verificări separate, care nu se condiționează automat una pe cealaltă:

- Dacă medicamentele intră sub coeficientul de perisabilitate aplicabil grupei lor de mărfuri (HG 831/2004), partea din pierdere care se încadrează în limita procentuală calculată la valoarea intrărilor e deductibilă fără altă condiție suplimentară de TVA.
- Dacă pierderea depășește limita HG 831/2004 sau nu se demonstrează încadrarea în ea, partea nedeductibilă la impozitul pe profit rămâne nedeductibilă indiferent de tratamentul TVA — cele două regimuri nu se anulează reciproc.

## Ce se greșește în practică

- Se presupune că orice marfă expirată distrusă scapă automat de ajustarea TVA, fără să existe dovada scrisă a distrugerii.
- Se confundă excepția de TVA (art. 304 alin. (2) lit. a)) cu deductibilitatea integrală a cheltuielii la impozitul pe profit — sunt verificări separate.
- Se distrug medicamentele fără proces-verbal sau altă probă opozabilă, pierzând posibilitatea de a invoca excepția în caz de control.

## Ce face iConta.eu

Motorul F066 (`core/perisabilitati.py`) calculează separarea 607 deductibil/nedeductibil pe baza procentului de limită introdus de contabil și generează linia de ajustare TVA (635=4426) doar pentru partea nedeductibilă, exact conform art. 304 alin. (1). Câmpul `degradare_dovedita_distrusa` din motor dezactivează explicit ajustarea TVA, indiferent de mărimea depășirii, atunci când degradarea calitativă și distrugerea sunt dovedite — dar decizia că dovada există (procesul-verbal de distrugere) rămâne o verificare documentară a contabilului, nu una automată a aplicației.

[iConta.eu](/)
