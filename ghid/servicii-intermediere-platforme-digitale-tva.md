---
title: "Servicii de intermediere prin platforme digitale: TVA 2026"
description: "Regula 'comisionarului' de TVA pentru servicii: o platformă care acționează în nume propriu, dar în contul altcuiva, este considerată ea însăși prestatoare a serviciului intermediat."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Servicii de intermediere prin platforme digitale: TVA 2026

Când o platformă digitală intermediază servicii între un prestator real și un beneficiar final, întrebarea esențială din perspectiva TVA nu e „cine face publicitate/serviciul efectiv", ci **în numele cui** acționează platforma față de client. Răspunsul schimbă complet lanțul de facturare.

## Temeiul legal

::: ghid-temei
„Atunci când o persoană impozabilă care acționează în nume propriu, dar în contul altei persoane, ia parte la o prestare de servicii, se consideră că a primit și a prestat ea însăși serviciile respective."
— Legea nr. 227/2015 (Codul fiscal), art. 271 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Norma metodologică ilustrează exact acest mecanism aplicat unei platforme de intermediere de servicii publicitare:

::: ghid-temei
„În sensul art. 271 alin. (2) din Codul fiscal, când pentru aceeași prestare de servicii intervin mai multe persoane impozabile care acționează în nume propriu, prin tranzacții succesive, indiferent de natura contractului, se consideră că fiecare persoană este cumpărător și revânzător, respectiv a primit și a prestat în nume propriu serviciul respectiv. [...] Exemplu: Societatea A prestează servicii de publicitate pentru produsele societății B. Serviciile sunt facturate către societatea C și aceasta le facturează către societatea B. Societatea C se consideră că a primit și a prestat în nume propriu servicii de publicitate."
— HG nr. 1/2016 pentru aprobarea Normelor metodologice de aplicare a Legii nr. 227/2015, pct. 8 alin. (2), Titlul VII (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

Aplicat la o platformă digitală de intermediere:

- Dacă platforma **emite facturi în nume propriu** către clientul final și **primește facturi în nume propriu** de la prestatorul real al serviciului, ea este tratată, din punct de vedere TVA, ca fiind ea însăși cumpărătoare și revânzătoare a serviciului — nu doar un simplu intermediar care facturează un comision.
- Fiecare verigă din lanț (prestator real → platformă → client final) se impozitează **separat**, ca o prestare distinctă de servicii, chiar dacă serviciul ajunge, în fapt, direct la beneficiarul final.
- Dacă platforma acționează transparent, ca simplu intermediar care facturează doar comisionul (fără să emită/primească facturi pe numele ei pentru serviciul de bază), regimul e diferit — se aplică structura de comision, nu cea de „cumpărător-revânzător".
- Această regulă e generală (art. 271 alin. (2)), aplicabilă serviciilor de orice tip intermediate prin platforme, nu doar publicității — inclusiv serviciilor digitale prestate prin platforme în 2026.

## Ce se greșește în practică

- Se presupune că o platformă care doar „găzduiește" tranzacția între prestator și client nu are nicio obligație de TVA proprie — dacă emite facturile pe numele ei, devine ea însăși parte impozabilă în lanț, conform art. 271 alin. (2).
- Se facturează greșit doar comisionul de intermediere, deși platforma a emis deja facturi în nume propriu pentru valoarea integrală a serviciului — structura fiscală trebuie să reflecte fluxul real de facturare, nu doar fluxul de bani.
- Se ignoră faptul că fiecare verigă a lanțului de intermediere se impozitează distinct — inclusiv atunci când sunt implicate trei sau mai multe platforme succesive.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are un modul specific pentru modelarea lanțurilor de intermediere prin platforme digitale** — aplicația tratează fiecare factură emisă sau primită ca o tranzacție individuală, pe baza datelor introduse de utilizator. Încadrarea corectă a rolului unei platforme (comisionar transparent vs. cumpărător-revânzător în nume propriu) rămâne o analiză a contabilului, care determină apoi cum se introduc facturile în aplicație.

[iConta.eu](/)
