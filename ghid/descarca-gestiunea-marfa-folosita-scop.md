---
title: "Cum se descarcă gestiunea pentru marfa folosită în scop propriu?"
description: "Regimul de TVA și descărcarea de gestiune când o firmă preia marfă din stoc pentru folosință proprie, fără să o vândă unui client."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se descărcă gestiunea pentru marfa folosită în scop propriu?

Când o firmă scoate din stoc o marfă pentru a o folosi ea însăși (nu pentru vânzare), operațiunea nu e „ieșire fără document" — legea o asimilează unei livrări de bunuri efectuate cu plată, dacă la achiziția mărfii s-a dedus TVA, integral sau parțial.

## Temeiul legal

::: ghid-temei
„Sunt asimilate livrărilor de bunuri efectuate cu plată următoarele operațiuni: a) preluarea de către o persoană impozabilă a bunurilor mobile achiziționate sau produse de către aceasta pentru a fi utilizate în scopuri care nu au legătură cu activitatea economică desfășurată, dacă taxa aferentă bunurilor respective sau părților lor componente a fost dedusă total sau parțial."
— Codul fiscal (Legea 227/2015), art. 270 alin. (4) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce presupune, concret, această regulă:

- Condiția care declanșează asimilarea cu o livrare taxabilă e dublă: bunul să fi fost preluat **pentru scopuri fără legătură cu activitatea economică** (folosință personală a asociatului/administratorului, de exemplu) și, la achiziția lui, TVA să fi fost **dedusă**, total sau parțial.
- Dacă ambele condiții sunt îndeplinite, firma trebuie să **colecteze TVA** pe valoarea bunului, exact ca la o vânzare normală, deși nu există niciun client și nicio încasare — de aceea operațiunea se numește „autolivrare" sau „livrare către sine".
- **Contabil**, gestiunea de marfă se descarcă la fel ca la o vânzare: 607 „Cheltuieli privind mărfurile" = 371 „Mărfuri" (la valoarea de înregistrare a mărfii ieșite), iar TVA colectată se înregistrează separat, pe seama unei cheltuieli (nu a unui client), pentru că nu există o creanță de încasat.
- Dacă bunul preluat pentru scop propriu se folosește totuși **în legătură cu activitatea economică** (de exemplu mostre, materiale consumabile folosite intern), sau dacă la achiziție nu s-a dedus deloc TVA, operațiunea nu se încadrează la art. 270 alin. (4) lit. a) — nu se colectează TVA suplimentar.

## Ce se greșește în practică

- Se scoate marfa din gestiune fără nicio notă contabilă („se pierde" din stoc), fără colectarea TVA aferentă — la un control, diferența se constată ca lipsă de gestiune nejustificată, cu tratament fiscal mai aspru decât autolivrarea declarată corect.
- Se presupune că autolivrarea se aplică doar bunurilor de folosință personală evidentă (autoturisme, electronice), ignorând orice bun preluat pentru un scop din afara activității economice, indiferent de natura lui.
- Se omite verificarea condiției deducerii TVA la achiziție — dacă bunul a fost cumpărat fără drept de deducere (de la un neplătitor, sau cu deducere exclusă prin lege), preluarea pentru scop propriu nu generează obligația de a colecta TVA suplimentar.

## Ce face iConta.eu

La data acestui ghid, iConta.eu oferă, prin modulul `core/stocuri.py` (gestiune global-valorică, funcția `descarcare_gv`) și prin evidența generală de stocuri, mecanismul de descărcare a gestiunii pe baza vânzărilor înregistrate — dar **nu am găsit** o funcționalitate dedicată care să identifice automat o preluare pentru scop propriu și să calculeze TVA colectată aferentă, potrivit art. 270 alin. (4) lit. a). Nota contabilă pentru o asemenea operațiune (607 = 371, plus TVA colectată) se înregistrează manual de contabil, folosind evidența contabilă generală a aplicației.

[iConta.eu](/)
