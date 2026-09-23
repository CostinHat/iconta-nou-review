---
title: Cota redusă de TVA la alimente și băuturi în 2026
description: Alimentele și băuturile destinate consumului uman și animal intră la cota redusă de 11%, dar cu patru excepții explicite care trec la 21% — băuturile alcoolice, băuturile NC 2202, alimentele cu zahăr adăugat ≥10g/100g și suplimentele alimentare.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cota redusă de TVA la alimente și băuturi în 2026

Livrarea de alimente și băuturi destinate consumului uman și animal beneficiază, ca regulă, de cota redusă de TVA de 11%. Legea nu lasă însă regula fără excepții: patru categorii ies explicit din cota redusă și trec la cota standard de 21%, indiferent cât de „aliment" pare produsul la prima vedere.

## Temeiul legal

::: ghid-temei
Cota redusă de 11% se aplică pentru „livrarea următoarelor bunuri: alimente, inclusiv băuturi, destinate consumului uman și animal, animale și păsări vii din specii domestice, ale căror coduri NC se stabilesc prin normele metodologice, cu excepția: 1. băuturilor alcoolice; 2. băuturilor nealcoolice care se încadrează la codul NC 2202; 3. alimentelor cu zahăr adăugat, al căror conținut total de zahăr este de minimum 10 g/100 g produs, altele decât laptele praf pentru nou-născuți, sugari și copii de vârstă mică; 4. suplimentelor alimentare definite de Legea nr. 56/2021 privind suplimentele alimentare" — Codul fiscal, art. 291 alin. (2) lit. b).
:::

## Regula și cele patru excepții

Cota de 11% se aplică livrării de bunuri — vânzarea la raft, în magazin, la piață, prin comerț online — a alimentelor și băuturilor pentru consum uman și animal. Ies din cota redusă și trec la 21%:

1. **Băuturile alcoolice** — orice băutură care conține alcool, fără prag minim.
2. **Băuturile nealcoolice de la codul NC 2202** — categoria vamală a apelor și băuturilor răcoritoare îndulcite/aromatizate.
3. **Alimentele cu zahăr adăugat ≥10g/100g produs** — cu o excepție în interiorul excepției: laptele praf pentru nou-născuți, sugari și copii de vârstă mică rămâne la 11% chiar dacă depășește pragul.
4. **Suplimentele alimentare** definite de Legea nr. 56/2021 — indiferent de conținutul de zahăr sau de faptul că se vând la raft alături de alimente obișnuite.

Legea 141/2025 a modificat această listă de la 1 august 2025 (Codul fiscal, art. 291 alin. (2), astfel cum a fost modificat de pct. 42, art. II din Legea nr. 141/2025), iar cotele rezultate — 21% standard / 11% redusă — rămân valabile pe tot parcursul lui 2026.

## Ce se greșește în practică

- Se aplică 11% pe toată factura unui furnizor de băuturi, fără verificarea codului NC — băuturile alcoolice și cele NC 2202 rămân la 21% indiferent de restul sortimentului facturat.
- Se ignoră pragul de zahăr la produsele dulci ambalate (sucuri, batoane, cereale îndulcite) — peste 10g/100g, cota corectă e 21%, nu 11%, cu excepția explicită a laptelui praf pentru copii mici.
- Se tratează suplimentele alimentare (pulberi proteice, capsule, vitamine) ca „alimente" la 11% — legea le exclude explicit din categoria redusă, indiferent de raionul unde se vând fizic.

## Ce face iConta.eu

`core/cote_tva.py` include categoria de alimente/băuturi la 11% în `CATEGORII_11`, cu cele patru excepții din `EXCEPTII_21` (băuturi alcoolice, băuturi NC 2202, alimente cu zahăr ≥10g/100g, suplimente alimentare Legea 56/2021) potrivite pe linia de factură. Dacă motorul de potrivire nu poate determina cu certitudine categoria unui produs, aplicația nu presupune tăcut 21% — răspunde cu un statut de cotă nedeterminată, care blochează emiterea până la o clasificare manuală, exact pentru a evita o cotă greșită pe o factură deja emisă.

[iConta.eu](/)
