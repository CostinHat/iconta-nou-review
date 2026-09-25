---
title: "Documentarea duratei de viață utilă a mijlocului fix"
description: "Cum se stabilește și se documentează durata normală de funcționare a unui mijloc fix, conform Catalogului mijloacelor fixe (HG 2139/2004)."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Documentarea duratei de viață utilă a mijlocului fix

Durata normală de funcționare a unui mijloc fix nu se alege liber — Catalogul mijloacelor fixe stabilește pentru fiecare categorie un interval minim-maxim de ani, iar alegerea concretă din acest interval trebuie documentată la punerea în funcțiune.

## Temeiul legal

::: ghid-temei
„Catalogul cuprinde clasificarea mijloacelor fixe utilizate în economie și duratele normale de funcționare ale acestora, care corespund cu duratele de amortizare în ani, aferente regimului de amortizare liniar. [...] Pentru stabilirea duratei normale de funcționare a unui mijloc fix se caută succesiv în clasificare: grupa, subgrupa, clasa, subclasa și familia, după caz. [...] La punerea în funcțiune a acestui mijloc fix, se va stabili durata normală de funcționare în limitele intervalului [...]. În cazul mijloacelor fixe achiziționate cu durata normală de funcționare expirată sau pentru care nu se cunosc datele de identificare, durata normală de funcționare se stabilește de către o comisie tehnică sau expert tehnic independent."
— HG 2139/2004, Anexă, Cap. I pct. 1 și Cap. II pct. 2 și Cap. III pct. 3 (sursă: anaf_surse/hg_2139_2004_catalog_clasificare_durate_mijloace_fixe.txt)
:::

Documentarea corectă presupune parcurgerea explicită a pașilor din catalog:

- Identificarea codului de clasificare al activului (grupă → subgrupă → clasă → subclasă →, unde e cazul, familie), pentru a găsi intervalul minim-maxim de ani aplicabil.
- Alegerea, **la momentul punerii în funcțiune**, a unei durate concrete în interiorul acestui interval — odată stabilită, durata rămâne neschimbată până la recuperarea integrală a valorii de intrare sau scoaterea din funcțiune.
- Pentru active care nu se regăsesc clar în catalog, sau achiziționate cu durata deja expirată ori fără informații de identificare, durata se stabilește prin **comisie tehnică sau expert tehnic independent** — nu la latitudinea liberă a contabilului.
- Reglementările contabile tratează durata de viață utilă ca o **estimare** (OMFP 1802/2014, pct. 70), ceea ce înseamnă că poate fi revizuită ulterior, dar revizuirea produce efecte doar prospectiv, nu retroactiv.

## Ce se greșește în practică

- Se alege o durată de amortizare arbitrară, fără verificarea intervalului minim-maxim din catalog pentru grupa/clasa corectă a activului.
- Nu se păstrează nicio documentație (proces-verbal, decizie de comisie tehnică) care să ateste alegerea concretă a duratei din interiorul intervalului legal — la un control, alegerea pare nefondată chiar dacă se încadrează formal în limite.
- Se folosește pentru active fără corespondent clar în catalog o durată „după ureche", în loc să se recurgă la comisie tehnică sau expert tehnic independent, așa cum cere explicit norma.

## Ce face iConta.eu

Am verificat în `core/repo_mijloace_fixe.py` și `core/mijloace_fixe_import_api.py`: aplicația **preia durata normală de funcționare (`dnf_luni`) ca dată introdusă de contabil**, la import sau manual, fără să o verifice față de intervalele minim-maxim din Catalogul mijloacelor fixe (HG 2139/2004) și fără să solicite sau să genereze vreun document justificativ (proces-verbal de comisie tehnică, de exemplu). Corectitudinea încadrării în catalog rămâne, la acest moment, o verificare manuală a contabilului.

[iConta.eu](/)
