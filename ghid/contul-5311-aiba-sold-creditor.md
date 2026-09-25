---
title: "Poate contul 5311 să aibă sold creditor?"
description: "De ce contul de casă (531/5311) nu poate avea, contabil, sold creditor — și ce înseamnă în practică un asemenea sold aparent."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Poate contul 5311 să aibă sold creditor?

Nu. Contul 531 „Casa" (uzual notat analitic 5311 pentru lei) este definit ca **cont de activ**, iar soldul lui reprezintă numerarul fizic existent în casierie la un moment dat. Numerarul nu poate fi negativ — deci, contabil, un „sold creditor" la 531 nu descrie o realitate economică posibilă, ci semnalează o eroare de înregistrare.

## Temeiul legal

::: ghid-temei
„GRUPA 53 «CASA» [...] Contul 531 «Casa» Cu ajutorul acestui cont se ține evidența numerarului aflat în casieria entității, precum și a mișcării acestuia, ca urmare a încasărilor și plăților efectuate. Contul 531 «Casa» este un cont de activ. [...] Soldul contului reprezintă numerarul existent în casierie."
— OMFP 1802/2014, Cap. 16 „Funcțiunea conturilor", Grupa 53, Contul 531 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Consecințele definiției „cont de activ":

- În debitul contului 531 se înregistrează **încasările** (numerar ridicat de la bancă, încasări de la clienți, aporturi, restituiri de avansuri etc.), iar în credit **plățile**.
- Soldul normal e debitor și reprezintă exact numerarul fizic din casă la acel moment — el trebuie să corespundă cu inventarul faptic al casieriei (registrul de casă zilnic).
- Un sold creditor la 531 ar însemna, tehnic, „numerar negativ" — o imposibilitate fizică. Când apare într-o balanță, cauza e aproape mereu o eroare de operare: o plată înregistrată fără să fi existat încasarea corespunzătoare în evidență, o notă contabilă cu conturile inversate (531 în loc de 401 sau invers), sau o închidere de lună înainte ca toate încasările zilei să fi fost introduse.

## Ce se greșește în practică

- Se lasă soldul creditor „temporar" în balanță, motivând că „se rezolvă luna viitoare" — între timp, orice raport generat din acea balanță (inclusiv declarații) pornește de la o cifră imposibilă.
- Se confundă eroarea de înregistrare cu o presupusă „plată în avans din casă" — casa nu poate finanța o plată pe care nu o are acoperită, spre deosebire de un cont bancar cu descoperit autorizat.
- Se corectează soldul creditor printr-o notă contabilă artificială pe alt cont (de regulă 455 sau 473), fără să se identifice întâi înregistrarea greșită care l-a produs — problema reapare la următoarea închidere.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu blochează automat** o înregistrare care ar duce contul 531/5311 pe sold creditor — nu am găsit în cod o validare dedicată pentru acest caz. Aplicația oferă evidența contabilă generală (jurnal, fișă de cont, balanță), din care un sold creditor la casă se poate observa vizual la verificarea balanței lunare, dar identificarea și corectarea notei contabile care l-a produs rămân în sarcina contabilului.

[iConta.eu](/)
