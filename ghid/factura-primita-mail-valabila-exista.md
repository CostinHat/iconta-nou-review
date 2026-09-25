---
title: "Factura primită pe e-mail mai este valabilă dacă există și în e-Factura?"
description: "Ce document are valoare fiscală în relația B2B din România de la obligativitatea RO e-Factura, conform Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Factura primită pe e-mail mai este valabilă dacă există și în e-Factura?

Multe firme încă primesc, în paralel cu factura din RO e-Factura, o copie pe e-mail sau pe hârtie de la furnizor. Întrebarea care apare des: care dintre cele două „contează" din punct de vedere fiscal?

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile alin. (1), pentru operațiunile realizate între persoane impozabile stabilite în România conform art. 266 alin. (2), sunt considerate facturi numai facturile care îndeplinesc condițiile prevăzute de Ordonanța de urgență a Guvernului nr. 120/2021 privind administrarea, funcționarea și implementarea sistemului național privind factura electronică RO e-Factura și factura electronică în România [...]."
— Legea 227/2015 (Codul fiscal), art. 319 alin. (1^1), introdus prin Legea 296/2023 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Răspunsul e clar din text: în relația B2B dintre firme stabilite în România, **doar factura transmisă prin sistemul RO e-Factura are calitatea de „factură"** din punct de vedere fiscal.

- Alin. (1) al aceluiași articol definește ca „facturi" documentele pe suport hârtie sau electronic care îndeplinesc condițiile generale — dar alin. (1^1), introdus special pentru relația B2B internă, **exclude** de la această calificare orice document care nu a trecut prin RO e-Factura.
- O factură trimisă pe e-mail, în PDF sau pe hârtie, în paralel cu una identică transmisă și acceptată prin RO e-Factura, **nu are valoare fiscală proprie** — documentul cu valoare de factură rămâne cel din sistemul național.
- Corolarul practic: dacă factura din e-mail diferă de cea din RO e-Factura (sumă, TVA, poziții), cea din e-Factura este cea care contează pentru deducerea TVA și pentru înregistrarea în contabilitate — nu varianta primită pe e-mail.
- Aceeași lege prevede și că utilizarea facturii electronice „face obiectul acceptării de către destinatar, cu excepția facturilor care îndeplinesc condițiile prevăzute de OUG 120/2021" — adică, pentru facturile obligatorii prin RO e-Factura, acceptarea nu mai e o formalitate separată.

## Ce se greșește în practică

- Se înregistrează în contabilitate factura primită pe e-mail, fără să se verifice dacă există și o versiune încărcată în RO e-Factura, riscând înregistrarea unui document fără valoare fiscală.
- Se presupune că „am primit factura pe e-mail, deci am dreptul de deducere", deși pentru operațiunile B2B interne dreptul de deducere se leagă de factura din sistemul național.
- Se ignoră situațiile de discrepanță între cele două variante (e-mail vs. e-Factura), fără să se sesizeze că valoarea corectă e cea din sistemul oficial.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are integrare completă cu sistemul RO e-Factura — trimitere, primire și descărcare automată prin conectorul SPV (`core/spv_conector.py`, `core/spv_receive.py`, `core/efactura_import.py`, `core/efactura_send.py`). Facturile procesate de aplicație provin din acest canal, tocmai facturile cu valoare fiscală potrivit art. 319 alin. (1^1) din Codul fiscal — nu din copiile trimise pe e-mail, care rămân în afara fluxului aplicației.

[iConta.eu](/)
