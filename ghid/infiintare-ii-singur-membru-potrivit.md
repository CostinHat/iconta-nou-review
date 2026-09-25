---
title: "Înființare II cu un singur membru: când e potrivit"
description: "Ce distinge, fiscal, o întreprindere individuală de o persoană fizică autorizată, și unde se oprește granița informației confirmate din sursele consultate pentru acest ghid."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Înființare II cu un singur membru: când e potrivit

Întreprinderea individuală (II) și persoana fizică autorizată (PFA) sunt forme diferite de organizare a unei activități economice fără personalitate juridică, dar fiscal sunt tratate identic: veniturile lor intră în aceeași categorie, „venituri din activități independente".

## Temeiul legal

::: ghid-temei
„Veniturile din activități independente cuprind veniturile din activități de producție, comerț, prestări de servicii și veniturile din profesii liberale, realizate în mod individual și/sau într-o formă de asociere, inclusiv din activități adiacente."
— Codul fiscal (Legea 227/2015), art. 67 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Notă onestă: distincția juridică propriu-zisă dintre PFA și întreprindere individuală (constituire, răspundere patrimonială, posibilitatea de a angaja personal) e reglementată prin OUG 44/2008 privind desfășurarea activităților economice de către persoanele fizice autorizate, întreprinderile individuale și întreprinderile familiale — act pe care **nu l-am găsit în sursele locale din `anaf_surse/`**, așa că nu citez din el text verbatim. Ce pot confirma din sursele consultate:

- Din perspectiva Codului fiscal (art. 67 alin. (1)), atât PFA, cât și întreprinderea individuală generează „venituri din activități independente" — regimul de impozitare a venitului (sistem real sau normă de venit, potrivit art. 69 din Codul fiscal, citat și în normele metodologice) e același pentru ambele forme.
- Cifra de afaceri consolidată a mai multor forme de organizare fără personalitate juridică deținute de aceeași persoană (PFA, întreprindere individuală, întreprindere familială) se **cumulează** atunci când se verifică plafoane legate de alte entități controlate de același titular (de exemplu la calculul plafonului de microîntreprindere al unei firme legate) — o mențiune care arată că, fiscal, ANAF privește aceste forme ca fiind legate de aceeași persoană, nu izolate.

## Ce se greșește în practică

- Se presupune că alegerea între PFA și II se face doar pe criterii fiscale — diferența relevantă (răspundere patrimonială, posibilitatea de a avea angajați, formalități de constituire) ține de dreptul comercial, nu de Codul fiscal.
- Se ignoră faptul că veniturile din activități independente pot fi impozitate fie pe sistem real, fie pe bază de normă de venit (pentru activitățile din nomenclatorul aprobat) — alegerea sistemului de impozitare e independentă de forma juridică (PFA sau II).
- Se tratează plafoanele fiscale ale unei II ca fiind complet separate de alte entități ale aceluiași titular, deși unele reguli (de exemplu la microîntreprinderi legate) cer verificarea cifrei de afaceri cumulate.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are un registru dedicat** persoanelor fizice, PFA-urilor sau întreprinderilor individuale — nu am găsit în cod o asemenea evidență. Aplicația generează declarația unică (D212) pe baza datelor introduse manual de contabil (`core/d212.py`), indiferent dacă venitul provine de la o PFA sau o întreprindere individuală — motorul de calcul e agnostic la forma juridică, tratând ambele ca surse de venituri din activități independente. Decizia privind forma de organizare potrivită rămâne una juridică și antreprenorială, în afara evidenței contabile oferite de aplicație.

[iConta.eu](/)
