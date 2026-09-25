---
title: "Stocuri acordate drept sponsorizare: cum se descarcă"
description: "Regimul TVA al stocurilor acordate cu titlu gratuit în cadrul unei sponsorizări: plafonul de 3 la mie din cifra de afaceri și condițiile în care nu se colectează taxă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Stocuri acordate drept sponsorizare: cum se descarcă

Când o firmă donează mărfuri sau produse finite unui beneficiar de sponsorizare (în loc de bani), operațiunea nu iese din sfera TVA automat — legea o tratează, în principiu, ca o livrare de bunuri cu titlu gratuit, asimilată unei livrări cu plată. Există însă o excepție condiționată de un plafon anual, pe care contabilul trebuie s-o urmărească separat de creditul fiscal de sponsorizare.

## Temeiul legal

::: ghid-temei
„bunurile acordate gratuit în cadrul acțiunilor de sponsorizare sau mecenat nu sunt considerate livrări de bunuri dacă valoarea totală în cursul unui an calendaristic se încadrează în limita a 3 la mie din cifra de afaceri constituită din operațiuni taxabile, scutite cu sau fără drept de deducere, precum și din operațiuni pentru care locul livrării/prestării este considerat a fi în străinătate potrivit prevederilor art. 275 și 278 din Codul fiscal. Încadrarea în plafon se determină pe baza datelor raportate prin deconturile de taxă depuse pentru un an calendaristic. Nu se iau în calcul pentru încadrarea în aceste plafoane sponsorizările și acțiunile de mecenat, acordate în numerar, și nici bunurile pentru care taxa nu a fost dedusă. Depășirea plafoanelor constituie livrare de bunuri cu plată, respectiv se colectează taxa. Taxa colectată aferentă depășirii se include în decontul întocmit pentru ultima perioadă fiscală a anului respectiv."
— HG 1/2016, pct. 7 alin. (12) lit. b) (norme de aplicare a art. 270 alin. (8) lit. c) din Codul fiscal) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

Din text rezultă mecanismul concret de urmărit la descărcarea din gestiune:

- **Plafonul e de 3 la mie (0,3%) din cifra de afaceri anuală** — calculată din operațiuni taxabile, scutite cu sau fără drept de deducere, plus cele cu locul livrării în străinătate — nu doar din cifra de afaceri taxabilă.
- **Se cumulează pe tot anul calendaristic**, nu pe fiecare sponsorizare separat — o firmă care face mai multe donații de stocuri în același an le însumează pentru a verifica dacă depășește plafonul.
- **Intră la calcul doar bunurile pentru care s-a dedus TVA** la achiziție — bunurile fără drept de deducere nu se iau în calcul, pentru că nu există taxă de "recuperat" prin colectare.
- **Sub plafon**: operațiunea nu e livrare de bunuri, deci nu se colectează TVA — stocul se descarcă la cost, fără autofactură de TVA.
- **Peste plafon**: depășirea devine livrare de bunuri cu plată, se colectează TVA prin autofactură, iar taxa colectată intră în decontul ultimei perioade fiscale a anului.

## Ce se greșește în practică

- Se descarcă stocul din gestiune fără să se verifice deloc plafonul de 3 la mie — se presupune, greșit, că orice bun donat pentru sponsorizare scapă automat de TVA.
- Se calculează plafonul raportându-l la cifra de afaceri taxabilă din decontul de TVA al lunii curente, în loc de cifra de afaceri cumulată pe tot anul calendaristic.
- Se include în calculul plafonului valoarea sponsorizărilor în bani — legea exclude explicit sumele acordate în numerar din verificarea acestui plafon, care privește doar bunurile.
- Se omite autofactura pentru depășirea de plafon, iar TVA colectată aferentă rămâne needeclarată în decontul de la finalul anului.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează **creditul fiscal de sponsorizare** (art. 25 alin. (4) lit. i) din Codul fiscal) în `core/sponsorizari.py`, prin funcția `credit_sponsorizare()`, dar înregistrarea contabilă suportată pentru sponsorizare (`nota_sponsorizare()`) acoperă doar varianta în bani — contul 6582 în corespondență cu 401 (pe contract) sau 5121 (plată directă). Nu există în cod nicio funcție dedicată descărcării de gestiune a stocurilor acordate pentru sponsorizare și nicio verificare automată a plafonului de 3 la mie din cifra de afaceri. Contabilul trebuie să urmărească manual acest plafon și să înregistreze separat autofactura de TVA în cazul depășirii.

[iConta.eu](/)
