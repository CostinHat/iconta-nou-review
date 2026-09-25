---
title: "Checklist de conformare pentru HoReCa 2026"
description: "Obligațiile specifice restaurantelor și barurilor în 2026: tratamentul bacșișului, cota de TVA pentru servicii de restaurant și bonul fiscal cu notă de plată, conform Legii 376/2022 și Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Checklist de conformare pentru HoReCa 2026

Restaurantele și barurile (CAEN 5610, 5630) au câteva obligații fiscale specifice care nu se regăsesc la alte activități: cota redusă de TVA pentru serviciile de restaurant, regimul distinct al bacșișului și obligația de a prezenta clientului o notă de plată cu rubrici pentru bacșiș, înainte de bonul fiscal.

## Temeiul legal

::: ghid-temei
„Prin bacșiș se înțelege orice sumă de bani oferită în mod voluntar de client, în plus față de contravaloarea bunurilor livrate sau a serviciilor prestate de către operatorii economici care desfășoară activități corespunzătoare codurilor CAEN: 5610 - «Restaurante», 5630 - «Baruri și alte activități de servire a băuturilor». Bacșișul nu poate fi asimilat, din punctul de vedere al TVA, unei livrări de bunuri sau unei prestări de servicii."
— Legea 376/2022 (care introduce art. 2^3 în OUG 28/1999), alin. (1) (sursă: anaf_surse/legea_376_2022_modificarea_completarea_ordonantei_urgenta_guvernului.txt)
:::

Checklist-ul de conformare specific HoReCa pentru 2026:

- **Nota de plată, obligatorie înainte de bonul fiscal**: trebuie să conțină rubrici pentru alegerea bacșișului **între 0% și 15%** din consumație, plus o rubrică pentru sumă fixă — indiferent de modalitatea de plată (card sau numerar); nu e obligatorie doar la livrarea la domiciliul clientului (Legea 376/2022 alin. (2), (3) și (5)).
- **Interdicția de condiționare**: e interzis să se condiționeze livrarea/prestarea de acordarea bacșișului (Legea 376/2022 alin. (4)).
- **Evidența și distribuirea integrală**: bacșișul se înregistrează în contabilitate pe un analitic distinct al conturilor de datorii și se distribuie integral salariaților, pe baza unei evidențe nominale — procedura de distribuire se stabilește printr-un regulament intern (Legea 376/2022 alin. (8)).
- **Regimul fiscal la salariat**: bacșișul distribuit e venit din alte surse, impozitat cu 10% (impozit final, reținut la sursă de firmă la momentul distribuirii, achitat până pe 25 a lunii următoare), **fără** contribuții sociale (CAS/CASS) și fără să poată fi reîncadrat ca venit salarial (Legea 376/2022 alin. (10) + Cod fiscal art. 115 alin. (1)-(3)).
- **Bacșișul evidențiat pe factură**, dacă se cere la cererea clientului, urmează alt regim — se înregistrează pe cheltuieli de protocol, cu regimul fiscal al acestora, nu cu impozitul de 10% pe venit din alte surse aplicabil distribuirii către salariați (Legea 376/2022 alin. (7)) — un traseu diferit de cel al bacșișului de pe bonul fiscal.
- **Cota de TVA pentru serviciile de restaurant și catering**: 11%, cu excepția băuturilor alcoolice și a băuturilor nealcoolice de la codul NC 2202, care rămân la cota standard (Cod fiscal art. 291 alin. (2) lit. n), în vigoare de la 01.08.2025).

## Ce se greșește în practică

- Se omite complet nota de plată cu rubricile pentru bacșiș (0-15% + sumă fixă), oferindu-se direct bonul fiscal — obligație legală distinctă, indiferent dacă bacșișul se plătește cu cardul sau cash.
- Se reține impozit pe venit din alte surse (10%) pe bacșiș, dar se plătesc și contribuții sociale (CAS/CASS) ca la salariu — legea exclude expres aplicarea titlului V (contribuții) și interzice reîncadrarea ca venit salarial.
- Se confundă bacșișul evidențiat pe factura emisă la cerere (tratat ca protocol) cu bacșișul de pe bonul fiscal distribuit salariaților (tratat ca venit din alte surse, impozit 10%) — cele două au regimuri diferite.
- Se aplică cota standard de TVA la toate serviciile de restaurant, uitând reducerea la 11% pentru mâncare (dar nu și pentru băuturile alcoolice sau cele de la codul NC 2202).

## Ce face iConta.eu

Funcționalitatea **Bacșiș HoReCa** generează notele contabile pentru încasarea bacșișului pe bonul fiscal (creanță internă de distribuit către salariați) și pentru distribuirea lui, cu reținerea automată a impozitului de 10% din suma brută și plata netului către salariat — respectă exact mecanismul din Legea 376/2022 alin. (8)-(10): sumele nu intră în veniturile firmei, iar impozitul e final, plătit prin D100 pe poziția dedicată bacșișului, confirmată în nomenclatorul ANAF.

Aplicația **nu acoperă** traseul de la alin. (7) — bacșișul evidențiat pe factura emisă la cererea clientului, tratat ca protocol — nu există un flux separat pentru acest caz în modulul de bacșiș. De asemenea, calculul cotei reduse de TVA (11%) pentru facturile de vânzare rămâne cel general al aplicației, ca la orice altă operațiune — nu există o validare specifică HoReCa care să semnaleze o factură de restaurant greșit taxată la cota standard.

[iConta.eu](/)
