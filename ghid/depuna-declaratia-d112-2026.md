---
title: "Cine trebuie să depună declarația D112 în 2026?"
description: "Cine are obligația legală de a depune lunar declarația 112 și ce s-a schimbat odată cu formularul aplicabil din veniturile lunii iulie 2026."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cine trebuie să depună declarația D112 în 2026?

Declarația 112 (Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate) e declarația lunară prin care orice angajator din România își raportează, într-un singur document, impozitul pe salarii, contribuțiile sociale reținute și datorate, și lista nominală a salariaților asigurați. Din veniturile lunii iulie 2026 se aplică o structură nouă a formularului, aprobată printr-un ordin comun al mai multor instituții.

## Temeiul legal

::: ghid-temei
„Persoanele fizice și juridice care au calitatea de angajatori sau sunt asimilate acestora, instituțiile prevăzute la art. 136 lit. d)-f), precum și persoanele fizice care realizează în România venituri din salarii sau asimilate salariilor de la angajatori din state care nu intră sub incidența legislației europene aplicabile în domeniul securității sociale [...] sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate."
— Legea 227/2015 (Codul fiscal), art. 147 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.html)
:::

- Obligația nu ține de mărimea firmei sau de numărul de salariați — un singur angajat, chiar cu contract part-time sau pe perioadă scurtă, declanșează obligația de depunere lunară.
- Termenul e fix: **până la data de 25 inclusiv a lunii următoare** celei pentru care s-au plătit veniturile (salariile din august se declară până pe 25 septembrie).
- Ordinul comun ANAF/CNPP/CNAS/ANOFM nr. 605/95/928/2314/2026 extinde explicit lista celor obligați și la persoanele fizice/instituțiile menționate la o serie întreagă de articole ale Codului fiscal (art. 68^1, 72, 84, 125, 147, 151, 169, 174, 174^1, 220 și 220^7) — practic orice categorie de plătitor de venituri asimilate salariilor, nu doar angajatorii „clasici".
- Depunerea se face obligatoriu **prin mijloace electronice de transmitere la distanță** (SPV/portalul ANAF), nu pe suport hârtie.
- Structura de formular aplicabilă în 2026 nu e uniformă pe tot anul: cea nouă (aprobată de ordinul 605/95/928/2314/2026) se aplică „începând cu declararea veniturilor aferente lunii iulie 2026"; pentru perioadele 1 ianuarie–30 iunie 2026 rămâne valabilă structura veche.

## Ce se greșește în practică

- Se presupune că obligația de depunere apare doar dacă firma are salariați cu normă întreagă pe tot parcursul lunii — de fapt, orice venit asimilat salariilor plătit în lună declanșează obligația, indiferent de durata sau tipul contractului.
- Se depune declarația pe structura veche și după 1 iulie 2026, din obișnuință — de la veniturile lunii iulie 2026 încolo, structura e cea nouă, validată pe schema tehnică actualizată.
- Se confundă termenul de depunere cu termenul de plată a contribuțiilor — ambele cad pe 25 ale lunii următoare, dar sunt obligații distincte (declarare vs. plată efectivă).

## Ce face iConta.eu

iConta generează declarația 112 pornind direct din datele de salarizare introduse în aplicație (stat de plată, concedii medicale, tichete), folosind același motor de calcul ca fluturașul de salariu, astfel încât cele două să nu poată diverge structural. XML-ul generat e validat local înainte de a fi arătat utilizatorului cu DUKIntegrator — validatorul oficial ANAF, rulat local, nu simulat — pe structura curentă aplicabilă (versiunea aliniată la Ordinul 605/95/928/2314/2026, pentru veniturile din iulie 2026 încolo).

Aplicația nu decide însă, în locul contabilului, **cine** are obligația de depunere — asta rămâne o evaluare legală pe care o face utilizatorul, pe baza situației reale a firmei (are sau nu salariați/venituri asimilate în luna respectivă). iConta generează declarația pentru firmele care au date de salarizare introduse; nu semnează și nu depune automat la ANAF — depunerea efectivă rămâne un pas separat, făcut de utilizator prin SPV, cu certificatul lui digital.

[iConta.eu](/)
