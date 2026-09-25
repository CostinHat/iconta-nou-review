---
title: "Divizarea firmei și păstrarea regimului micro"
description: "De ce divizarea unei firme pentru a rămâne sub plafonul de venituri al microîntreprinderilor nu funcționează așa cum se crede."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Divizarea firmei și păstrarea regimului micro

Când o firmă se apropie de plafonul de venituri al microîntreprinderilor, tentația de a o împărți în două entități mai mici, fiecare sub plafon, apare frecvent. Legea a fost scrisă tocmai ca să închidă această portiță — prin regula veniturilor cumulate ale întreprinderilor legate.

## Temeiul legal

::: ghid-temei
„(1^1) În aplicarea prevederilor alin. (1) lit. c) limita privind veniturile realizate se verifică luând în calcul veniturile realizate de persoana juridică română, cumulate cu veniturile întreprinderilor legate cu aceasta [...]. În sensul prezentului titlu, persoana juridică română este legată cu o altă persoană dacă există oricare dintre următoarele raporturi: a) persoana juridică română care verifică condiția deține la o altă persoană juridică română, direct și/sau indirect, peste 25% din valoarea/numărul titlurilor de participare sau al drepturilor de vot [...]; b) persoana juridică română care verifică condiția este deținută de o altă persoană juridică română, direct și/sau indirect, cu peste 25% [...]; c) persoana juridică română care verifică condiția este legată cu o altă persoană juridică română dacă o persoană deține, în mod direct și/sau indirect, peste 25% [...] atât la prima persoană juridică, cât și la cea de-a doua persoană juridică."
— Legea nr. 227/2015 (Codul fiscal), art. 47 alin. (1^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul e simplu, dar rareori intuit corect:

- Pragul de venituri pentru încadrarea ca microîntreprindere (art. 47 alin. (1) lit. c)) **nu se verifică izolat, pe fiecare firmă în parte**, ci cumulat cu veniturile tuturor „întreprinderilor legate" — adică firme între care există o legătură de deținere de peste 25% din titluri/drepturi de vot, directă sau indirectă.
- O divizare care păstrează asociații/acționarii comuni peste pragul de 25% **nu scoate firmele rezultate de sub obligația de cumulare** — veniturile lor se adună în continuare pentru verificarea plafonului.
- Legătura e definită și indirect (lit. c) — dacă o a treia persoană deține peste 25% în ambele firme rezultate din divizare, cumularea se aplică oricum.

## Ce se greșește în practică

- Se divizează firma exact la pragul plafonului, considerând că fiecare entitate nouă „pornește de la zero" fiscal — dar veniturile lor rămân cumulate atâta timp cât asociații comuni dețin peste 25% în ambele.
- Se ignoră legătura indirectă (prin intermediul unei a treia persoane juridice sau al unei persoane fizice autorizate a aceluiași asociat) — regula acoperă și aceste situații.
- Se tratează cumularea ca pe o simplă sumă a cifrelor de afaceri, ignorând condiția de fond — verificarea existenței efective a raportului de „întreprinderi legate" la data de referință.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are o funcționalitate care să calculeze automat veniturile cumulate ale întreprinderilor legate** pentru verificarea încadrării la microîntreprindere — nu am găsit în cod nicio logică legată de pragul de 25% din titluri de participare sau de identificarea firmelor afiliate. Mai mult, nici plafonul de 100.000 euro pentru firma proprie, izolat, nu este verificat automat — nu există, la acest moment, o constantă sau un modul dedicat acestui plafon; dacă firma face parte dintr-un grup cu asociați comuni peste pragul de 25%, verificarea cumulării rămâne, ca și restul verificării plafonului, responsabilitatea contabilului.

[iConta.eu](/)
