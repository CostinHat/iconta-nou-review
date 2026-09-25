---
title: "Cum se configurează cronul de sincronizare WooCommerce?"
description: "Nu există o opțiune de configurare a orarului de sincronizare — ce se configurează, de fapt, e magazinul online (URL și chei API); frecvența automată e fixă, la nivel de sistem."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se configurează cronul de sincronizare WooCommerce?

Întrebarea pornește de la o premisă care nu se confirmă în practică: nu există o setare, un ecran sau o opțiune prin care un utilizator să aleagă sau să modifice ora/frecvența la care rulează sincronizarea automată cu magazinul online. Ce se poate configura, de fapt, este magazinul în sine — adresa lui și cheile de acces API — nu programarea automată.

## Temeiul legal

::: ghid-temei
„Pentru alte operațiuni decât cele prevăzute la alin. (15), persoana impozabilă are obligația de a emite o factură cel târziu până în cea de-a 15-a zi a lunii următoare celei în care ia naștere faptul generator al taxei, cu excepția cazului în care factura a fost deja emisă."
— Codul fiscal (Legea nr. 227/2015), art. 319 alin. (16) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Legea stabilește un termen-limită de emitere a facturii, nu o metodă sau o frecvență obligatorie de generare a ei — modul în care o firmă își organizează facturarea (manual, automat, zilnic, la cerere) e o alegere operațională, nu o cerință legală.
- Din perspectivă legală, contează doar ca fiecare comandă onorată să ajungă, până la urmă, la o factură emisă în termen — nu contează dacă acest lucru s-a întâmplat printr-o rulare automată programată de furnizorul aplicației sau printr-o acțiune manuală a utilizatorului.

## Ce se greșește în practică

- Se caută în aplicație o secțiune de „setări cron" sau „program de sincronizare", presupunând că frecvența automată e o opțiune per firmă — de regulă, într-un astfel de sistem, orarul e o proprietate fixă a infrastructurii, comună tuturor utilizatorilor, nu o setare individuală.
- Se confundă „a configura magazinul" (adresă + chei de acces) cu „a configura cronul" — primul depinde de utilizator, al doilea nu.
- Se amână configurarea propriu-zisă a conectorului (singura acțiune reală disponibilă) în așteptarea unei opțiuni de „programare" care nu există.

## Ce face iConta.eu

Verificat direct în cod și în rutele aplicației: iConta.eu **nu oferă nicio rută, ecran sau opțiune de configurare a orarului de sincronizare**, nici per firmă, nici global. Ce există efectiv, din ecranul „Magazin online":

- configurarea conectorului — URL-ul magazinului și cheile Consumer Key/Consumer Secret, salvate per firmă;
- butonul „Sincronizează acum", pentru declanșarea manuală a sincronizării, oricând.

Programarea automată (rularea zilnică, la o oră fixă) e o proprietate a sistemului, identică pentru toate firmele care au magazinul configurat, și nu poate fi ajustată din aplicație. Din momentul în care conectorul e configurat corect, sincronizarea automată zilnică preia comenzile fără nicio setare suplimentară din partea utilizatorului — deci întrebarea corectă de pus nu e „cum configurez cronul", ci „cum configurez magazinul, ca să beneficiez de sincronizarea automată existentă".

[iConta.eu](/)
