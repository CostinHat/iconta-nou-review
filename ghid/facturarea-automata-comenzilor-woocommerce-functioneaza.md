---
title: "Facturarea automată a comenzilor WooCommerce: cum funcționează?"
description: "Facturarea automată din comenzi WooCommerce rulează printr-un proces de sistem zilnic, separat de ecranul de configurare a magazinului online, și ajută la încadrarea în termenul legal de emitere a facturii."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Facturarea automată a comenzilor WooCommerce: cum funcționează?

Cuvântul „automată" e cheia întrebării: comportamentul descris aici — transformarea comenzilor în facturi fără nicio acțiune a utilizatorului, în fiecare zi — este produs de un proces de sistem separat, nu de ecranul manual de configurare a magazinului online. Legal, motivul practic pentru care o automatizare zilnică ajută e simplu: factura tot trebuie emisă într-un termen fix, indiferent de cât de des se verifică manual magazinul.

## Temeiul legal

::: ghid-temei
„Pentru alte operațiuni decât cele prevăzute la alin. (15), persoana impozabilă are obligația de a emite o factură cel târziu până în cea de-a 15-a zi a lunii următoare celei în care ia naștere faptul generator al taxei, cu excepția cazului în care factura a fost deja emisă."
— Codul fiscal (Legea nr. 227/2015), art. 319 alin. (16) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Legea nu impune o frecvență anume de facturare a comenzilor unui magazin online — impune doar termenul-limită de emitere, calculat de la faptul generator (livrarea/prestarea).
- O rulare zilnică automată e o alegere de produs care reduce riscul de a depăși acest termen, nu o cerință legală în sine.
- Emiterea facturii rămâne responsabilitatea firmei, indiferent dacă e făcută printr-un proces automat sau manual.

## Ce se greșește în practică

- Se confundă ecranul de configurare a magazinului online (unde se introduc URL-ul și cheile API) cu mecanismul care declanșează efectiv facturarea automată — sunt două componente diferite ale aceluiași sistem.
- Se presupune că orarul rulării automate poate fi ales sau ajustat de utilizator — în multe implementări de acest tip, orarul e o proprietate fixă a procesului de sistem, nu o setare per firmă.
- Se așteaptă ca rularea automată să acopere și comenzi cu statusuri „intermediare" (neconfirmate, în așteptarea plății) — de regulă, procesul automat citește doar comenzile deja finalizate.

## Ce face iConta.eu

În iConta.eu, cele două componente sunt distincte, confirmat direct în cod și în ruta de configurare:

- **Configurarea magazinului online** (URL + chei API) și butonul **„Sincronizează acum"** se fac din ecranul „Magazin online" — declanșare **manuală**, de către utilizator, cu rol de administrator al firmei.
- **Facturarea automată propriu-zisă** rulează separat, printr-un proces de sistem programat zilnic la 07:30, care reutilizează același motor de transformare comandă → factură, dar iterează automat toate firmele cu magazinul configurat, fără nicio acțiune din partea utilizatorului. Chiar ecranul de configurare informează despre acest comportament, ca notă: „Comenzile din WooCommerce devin facturi emise automat (zilnic la 07:30)."

Comportamentul de facturare automată descris în acest titlu ține, așadar, de acest proces zilnic de sistem, nu de ecranul de configurare manuală a conectorului. Regulile de filtrare (statusul comenzii, evitarea duplicatelor) sunt identice în ambele cazuri, pentru că folosesc același motor.

[iConta.eu](/)
