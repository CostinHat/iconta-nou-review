---
title: Când se plătesc contribuții la nivelul salariului minim pentru part-time?
description: Când brutul contractual al unui part-time scade sub o „podea" minimă — salariul minim redus cu facilitatea aplicabilă, proratat pe fracțiunea de normă — CAS și CASS se calculează la acel nivel minim, nu pe brutul real.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Când se plătesc contribuții la nivelul salariului minim pentru part-time?

La normă parțială, brutul contractual poate fi mic, proporțional cu timpul lucrat. Dar legea nu permite ca CAS și CASS să scadă oricât — există o podea minimă. Când brutul contractual scade sub această podea, contribuțiile se calculează la nivelul podelei, nu la brutul real primit de angajat.

## Temeiul legal

::: ghid-temei
Contribuția CAS „nu poate fi mai mică" decât CAS calculat pe salariul minim, „în baza unui contract individual de muncă cu normă întreagă SAU cu timp parțial" — condiția e venitul sub minim, nu norma de lucru. — Codul fiscal, art.146 alin.(5^6)
:::

## Cum se calculează podeaua

Podeaua de referință = (salariul minim al perioadei − facilitatea aplicabilă perioadei) × fracțiunea de normă. Modul de proratare (scăderea facilității din nivelul de referință, apoi proratarea pe fracțiunea de normă) e o interpretare aplicată de echipa iConta.eu, confirmată de regula validatorului oficial DUK (`SP1B4_1`), dar nu e literă explicită a legii — textul OUG-urilor privind facilitatea vorbește despre reducerea „nivelului" cu 300/200 lei, fără să precizeze dacă acea reducere se aplică și podelei de la part-time.

## Când se declanșează regula

Regula se declanșează exact când brutul contractual e sub podeaua calculată mai sus. Exemplu, pentru un contract part-time la 4 ore/zi (fracțiune 0,5), fereastra 1 iulie – 31 decembrie 2026 (salariul minim 4.325 lei, facilitate 200 lei), cu un brut contractual de 2.000 lei:

- Podea = (4.325 − 200) × 0,5 = 2.062,50 lei
- Brutul contractual (2.000 lei) e sub podea (2.062,50 lei) → se aplică regula.

Dacă, în schimb, brutul contractual ar fi fost 2.162,50 lei (exact salariul minim proporțional cu norma), ar fi fost peste podea și regula nu s-ar fi aplicat — contribuțiile s-ar fi calculat direct pe brut.

## Cine suportă diferența

Angajatul e reținut cu CAS/CASS calculate pe brutul lui real (cel mai mic): CAS = 25% × 2.000 = 500 lei, CASS = 10% × 2.000 = 200 lei. Diferența până la nivelul podelei — CAS 25% × 2.062,50 = 515,63 lei, CASS 10% × 2.062,50 = 206,25 lei — nu se reține suplimentar din venitul angajatului. Structura conturilor confirmate în cod (421/4315 și 421/4316 pentru reținerea obișnuită, plus 6451/4315 și 6453/4316, conturi de cheltuială, pentru suprataxarea part-time) arată că diferența e suportată de angajator, ca o cheltuială suplimentară proprie: 15,63 lei la CAS, 6,25 lei la CASS.

## Ce se greșește în practică

Greșeala frecventă e aplicarea podelei pe salariul minim întreg, neproratat pe fracțiunea de normă — ceea ce suprataxează inutil un contract part-time. Greșeala inversă: se calculează contribuțiile direct pe brutul contractual redus, fără să se verifice deloc podeaua — ceea ce poate duce la contribuții sub nivelul minim legal, un risc semnalat inclusiv de refuzul D112 pentru date suspecte la brut sub minimul pe normă întreagă (chiar dacă, la part-time, comparația corectă e cu podeaua proratată, nu cu minimul întreg).

## Ce face iConta.eu

Regula „baza_podea" (`core/salarizare.py`, liniile 292-323) verifică automat, pentru fiecare stat de plată, dacă brutul contractual e sub podeaua calculată pentru fereastra activă a lunii, și generează notele contabile de suprataxare (6451/4315, 6453/4316) doar când e cazul. Interpretarea privind proratarea e documentată explicit în cod și în `core/registru_interpretari.py` (cheia `podea_part_time_minus_facilitate`), pentru trasabilitate.

[iConta.eu](/)
