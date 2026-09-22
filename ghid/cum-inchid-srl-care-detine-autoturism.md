---
title: Cum închid un SRL care deține un autoturism?
description: Vânzarea autoturismului către un terț la lichidare se tratează ca o livrare normală cu TVA pe prețul obținut, dar predarea lui directă către asociat este o livrare asimilată, taxabilă cu TVA la valoarea de piață — iar iConta.eu nu are o operațiune dedicată pentru acest al doilea caz.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum închid un SRL care deține un autoturism?

La lichidarea unui SRL care deține un autoturism (sau orice alt mijloc fix), tratamentul fiscal depinde decisiv de ce se întâmplă cu bunul: dacă se vinde unui terț, e o vânzare obișnuită; dacă se predă direct asociatului, ca parte a partajului, legea o tratează ca pe o livrare de bunuri cu plată, chiar dacă nu există niciun preț încasat.

## Temeiul legal

::: ghid-temei
**Cod fiscal 227/2015, art.270 alin.(5):**
"Orice distribuire de bunuri din activele unei persoane impozabile către asociații sau acționarii săi, inclusiv o distribuire de bunuri legată de lichidarea sau de dizolvarea fără lichidare a persoanei impozabile, cu excepția transferului prevăzut la alin. (7), constituie livrare de bunuri efectuată cu plată, dacă taxa aferentă bunurilor respective sau părților lor componente a fost dedusă total sau parțial."
:::

## Vânzare către un terț vs. predare directă către asociat

Dacă autoturismul este **vândut unui terț** în timpul lichidării, operațiunea e o vânzare normală de mijloc fix: se emite factură cu TVA colectată pe prețul de vânzare, iar valoarea rămasă neamortizată se descarcă din gestiune.

Dacă autoturismul este **predat direct asociatului** (de exemplu ca parte a partajului, în loc să fie vândut și transformat în bani), operațiunea nu mai e o simplă restituire — este, potrivit art.270 alin.(5), o livrare asimilată unei livrări cu plată, dacă TVA a fost dedusă la achiziție (total sau parțial). TVA se calculează la **valoarea de piață** a bunului la momentul predării, nu la valoarea contabilă rămasă și nu la un preț simbolic.

::: ghid-exemplu
Un autoturism cu valoare de piață estimată la predare de 50.000 lei, pentru care firma a dedus integral TVA la achiziție. Predarea directă către asociat generează TVA colectată de 50.000 lei × cota de TVA standard aplicabilă la data operațiunii (de verificat, nu presupusă fixă — de exemplu, ipotetic, la o cotă de 19% ar rezulta 9.500 lei), deși nu există nicio încasare efectivă — este un autoconsum/livrare asimilată, nu o vânzare.
:::

## Ce se greșește în practică

- Se crede că predarea autoturismului către asociat e neimpozabilă din TVA, pentru că "oricum e al lor, e doar o formalitate".
- Se folosește nota de vânzare a activului cu un preț fictiv sau simbolic, în loc să se calculeze corect TVA la valoarea de piață, ca livrare asimilată.
- Se calculează TVA la valoarea contabilă netă (rămasă după amortizare) în loc de valoarea de piață reală a bunului.
- Se ignoră condiția din art.270 alin.(5): dacă TVA nu a fost dedusă deloc la achiziția bunului, asimilarea nu se aplică.

## Ce face iConta.eu

iConta.eu oferă o singură operațiune pentru mijloace fixe la lichidare: nota de vânzare a activului (`nota_vanzare_activ`), care presupune întotdeauna o vânzare cu preț — generează `461=7583+4427` (venit din vânzare + TVA colectată pe prețul dat) și descărcarea din gestiune `6583+28xx=21x`. Cota de TVA este obligatorie la fiecare notă (aplicația nu are o valoare implicită), tocmai pentru ca operațiunea să reflecte cota reală în vigoare la data ei.

Aplicația **nu are o operațiune dedicată pentru distribuirea în natură** a unui activ direct către asociat, tratată ca livrare asimilată la valoarea de piață conform art.270 alin.(5). Dacă autoturismul e predat direct asociatului, contabilul trebuie să calculeze manual TVA la valoarea de piață și să înregistreze operațiunea prin motorul general de facturare al aplicației, nu prin nota de lichidare.

[iConta.eu](/)
