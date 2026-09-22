---
title: Ce registre trebuie să țină un PFA în sistem real?
description: Un PFA la sistem real ține obligatoriu Registrul-jurnal de încasări și plăți și Registrul-inventar, plus Registrul de evidență fiscală și Fișa mijlocului fix dacă are active amortizabile.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce registre trebuie să țină un PFA în sistem real?

PFA-ul (și, la fel, întreprinderea individuală sau familială) care determină venitul net în sistem real conduce contabilitatea în partidă simplă, nu contabilitate în partidă dublă ca o societate. Asta înseamnă un set de registre precis, definit prin lege — nu orice evidență proprie sau tabel Excel improvizat.

## Temeiul legal

::: ghid-temei
OMFP 170/2015, Cap. I, pct. 1: "persoanele fizice şi asocierile fără personalitate juridică, ale căror venituri sunt supuse impozitului pe venit ... al căror venit net anual este determinat în sistem real, pe baza datelor din contabilitate ... Persoanele care desfăşoară activități independente ... sunt persoanele care obțin venituri din: a.1 - activități economice (persoane fizice autorizate, întreprinderi individuale şi întreprinderi familiale) ..."

OMFP 170/2015, Cap. III, pct. 9: "Pentru evidențierea în contabilitatea în partidă simplă a operațiunilor efectuate se utilizează următoarele registre contabile: Registrul-jurnal de încasări şi plăți (cod 14-1-1/b) şi Registrul-inventar (cod 14-1-2/b), prevăzute la cap. V."

OMFP 170/2015, Cap. III, pct. 17: "Evidența imobilizărilor corporale (mijloace fixe) se ține cu ajutorul Fişei mijlocului fix (cod 14-2-2)."

Codul fiscal, art. 68 alin. (8): "Contribuabilii pentru care determinarea venitului anual se efectuează în sistem real au obligația să completeze Registrul de evidență fiscală, în vederea stabilirii venitului net anual."

OMFP 170/2015, Cap. IV, pct. 2: "Termenul de păstrare a Registrului-jurnal de încasări şi plăți (cod 14-1-1/b) şi a Registrului-inventar (cod 14-1-2/b) este de 10 ani."
:::

## Cele patru evidențe obligatorii

1. **Registrul-jurnal de încasări și plăți** (cod 14-1-1/b) — registrul de bază: fiecare încasare și fiecare plată, în numerar sau prin bancă, în ordine cronologică, totalizate lunar.
2. **Registrul-inventar** (cod 14-1-2/b) — se completează la începutul activității, la sfârșitul exercițiului financiar și la încetarea activității; cuprinde toate activele și datoriile din patrimoniul afacerii.
3. **Registrul de evidență fiscală** — obligatoriu prin Codul fiscal, distinct de registrele contabile de mai sus, servește strict la stabilirea venitului net anual (baza de calcul pentru Declarația Unică).
4. **Fișa mijlocului fix** (cod 14-2-2) — obligatorie doar dacă PFA-ul deține mijloace fixe amortizabile (echipamente, autoturisme, mobilier peste pragul valoric legal).

Toate patru se păstrează minimum 10 ani, la fel ca documentele justificative pe baza cărora au fost completate.

## Ce se greșește în practică

- Se ține doar un tabel cu încasări și cheltuieli, fără să se completeze deloc Registrul-inventar, considerat "opțional" — nu este.
- Se confundă Registrul de evidență fiscală cu Registrul-jurnal de încasări și plăți — sunt documente separate, cu scopuri diferite.
- Nu se completează Fișa mijlocului fix pentru fiecare activ amortizabil în parte, ci se ține doar o listă generală.
- Se arhivează registrele doar 5 ani, prin analogie cu alte documente fiscale, în loc de 10 ani cât cere explicit OMFP 170/2015.
- Se renunță la Registrul-inventar la încetarea activității, deși legea cere completarea lui tocmai "cu ocazia încetării activității".

## Ce face iConta.eu

Modulul `core/rip_api.py` generează automat Registrul-jurnal de încasări și plăți: funcția `lista(conn, schema, an, luna=None, status=None)` citește operațiunile anului, calculează `total_incasari`, `total_plati` și `sold`, iar sumele se pot totaliza lunar direct din aplicație. Funcția `registru_inventar(conn, schema, an)` construiește Registrul-inventar (cod 14-1-2/b), însumând mijloacele fixe la valoare rămasă (calculată prin amortizare liniară) cu disponibilitățile bănești (soldul validat cumulat al Registrului-jurnal până la 31.12), rezultând totalul activului. Fiecare operațiune introdusă în registru pornește cu statusul `ciorna` și devine parte din calculul fiscal abia după ce este trecută în `validata`, ceea ce lasă contabilului controlul final asupra a ceea ce intră în evidență.

[iConta.eu](/)
