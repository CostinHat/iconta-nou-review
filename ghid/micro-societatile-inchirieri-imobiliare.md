---
title: "Micro pentru societățile de închirieri imobiliare"
description: "De ce activitatea de închirieri imobiliare nu e exclusă de la impozitul micro — lista limitativă a domeniilor excluse din art. 47 alin. (3) Cod fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Micro pentru societățile de închirieri imobiliare

O societate ale cărei venituri provin din închirierea de spații (birouri, apartamente, spații comerciale) poate aplica impozitul micro — activitatea de închirieri imobiliare nu figurează printre domeniile excluse explicit de Codul fiscal.

## Temeiul legal

::: ghid-temei
„Nu intră sub incidența prezentului titlu următoarele persoane juridice române: a) Fondul de garantare a depozitelor în sistemul bancar [...]; b) Fondul de compensare a investitorilor [...]; c) Fondul de garantare a pensiilor private [...]; d) Fondul de garantare a asiguraților [...]; e) entitatea transparentă fiscal cu personalitate juridică; f) persoana juridică română care desfășoară activități în domeniul bancar; g) persoana juridică română care desfășoară activități în domeniul asigurărilor și reasigurărilor, al pieței de capital [...]; h) persoana juridică română care desfășoară activități în domeniul jocurilor de noroc; i) persoana juridică română care desfășoară activități de explorare, dezvoltare, exploatare a zăcămintelor de petrol și gaze naturale."
— Legea 227/2015, art. 47 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Lista de excluderi de la art. 47 alin. (3) e limitativă — nu poate fi extinsă prin interpretare la alte domenii de activitate. Închirierile imobiliare nu apar în ea, deci o societate din acest domeniu urmează regulile generale de eligibilitate de la art. 47 alin. (1): venituri sub 100.000 euro (redus prin OUG 8/2026), capital deținut de altcineva decât statul, firma nu e în dizolvare/lichidare, are cel puțin un salariat, asociații nu dețin peste 25% și în alte microîntreprinderi, iar situațiile financiare au fost depuse în termen. Veniturile din chirii (contul 706) intră în cifra de afaceri și în baza de calcul a impozitului micro ca orice alt venit din activitatea de bază.

## Ce se greșește în practică

- Se presupune, greșit, că activitatea de închirieri imobiliare are un regim special sau e exclusă de la micro, prin confuzie cu regimul TVA al chiriilor (care poate implica opțiune de taxare) sau cu impozitul pe clădiri.
- Se ignoră faptul că un asociat cu peste 25% din capitalul social al mai multor societăți de închirieri imobiliare (situație frecventă la portofolii de proprietăți divizate pe firme separate) declanșează obligația de la art. 47 alin. (1) lit. h) de a desemna o singură firmă eligibilă pentru micro.
- Se calculează plafonul de 100.000 euro fără a cumula veniturile firmelor legate (art. 47 alin. 1^1), relevant frecvent la grupurile de firme imobiliare cu proprietari comuni.

## Ce face iConta.eu

iConta.eu emite facturi de chirie și evidențiază contabil veniturile din chirii (funcția `nota_chirie_incasata` din `core/comodat_chirii.py`, care generează nota 4111 = 706 + 4427), atât pentru chiriile facturate de firmă, cât și pentru chiriile plătite de firmă unei persoane fizice (funcția `nota_chirie_platita`, care generează 612 = 462, fără TVA și fără reținere la sursă, contribuabilul persoană fizică declarându-și singur venitul prin Declarația Unică). La data acestui ghid, aplicația nu are o verificare dedicată a condițiilor de eligibilitate pentru micro (art. 47) specifică societăților de închirieri imobiliare — încadrarea rămâne o decizie manuală a contabilului, pe baza regulilor generale.

[iConta.eu](/)
