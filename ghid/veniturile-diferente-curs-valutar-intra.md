---
title: "Veniturile din diferențe de curs valutar intră în plafonul micro?"
description: "Cum se calculează plafonul de 100.000 euro pentru încadrarea ca microîntreprindere și de ce veniturile din diferențe de curs valutar nu intră în el."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Veniturile din diferențe de curs valutar intră în plafonul micro?

Nu. Plafonul care decide dacă o firmă rămâne sau devine microîntreprindere se calculează pe cifra de afaceri, în sensul reglementărilor contabile — nu pe totalul veniturilor înregistrate în contabilitate. Diferențele de curs valutar (cont 765) sunt venituri financiare, nu venituri din activitatea curentă, deci nu se adună la plafon.

## Temeiul legal

::: ghid-temei
„c) a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile; [...] (1^1) În aplicarea prevederilor alin. (1) lit. c) limita privind veniturile realizate se verifică luând în calcul veniturile realizate de persoana juridică română, cumulate cu veniturile întreprinderilor legate cu aceasta, iar veniturile care se iau în calcul sunt cele care constituie cifra de afaceri definită potrivit reglementărilor contabile aplicabile [...]"
— Legea 227/2015 (Codul fiscal), art. 47 alin. (1) lit. c) și alin. (1^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Condiția de plafon pentru încadrarea ca microîntreprindere se verifică pe **cifra de afaceri**, așa cum e definită de reglementările contabile aplicabile (OMFP 1802/2014), nu pe „veniturile din orice sursă" folosite mai departe la calculul impozitului.
- Cifra de afaceri netă cuprinde veniturile din vânzarea de produse și prestarea de servicii, din activitatea curentă a firmei — categorie care **nu include veniturile financiare** precum dobânzile sau diferențele de curs valutar (cont 765).
- Plafonul de 100.000 euro se cumulează, dacă e cazul, cu veniturile întreprinderilor legate — dar tot pe definiția de cifră de afaceri, nu pe totalul contabil.
- Cursul folosit pentru conversia în euro a plafonului e cel de la închiderea exercițiului financiar, nu cursul zilnic folosit intern pentru reevaluarea soldurilor valutare.

## Ce se greșește în practică

- Se confundă „venituri realizate" din art. 47 cu totalul rulajului creditor al conturilor de venituri din balanța de verificare, incluzând din greșeală conturile 765 și 766.
- Se calculează plafonul la un curs greșit — cel din ultima zi a lunii, folosit pentru reevaluarea lunară a soldurilor valutare, în loc de cursul de la închiderea exercițiului financiar, cerut explicit de lege pentru conversia plafonului.
- Se ignoră obligația de cumulare cu veniturile întreprinderilor legate, atunci când firma face parte dintr-un grup cu structură de deținere de peste 25%.

## Ce face iConta.eu

Funcționalitatea de diferențe de curs valutar din iConta.eu (`core/diferente_curs.py`) este, așa cum spune chiar codul, un „motor pur" de contabilizare pe conturile 665/765 — calculează suma diferenței și generează nota contabilă, la decontare sau la reevaluarea lunară a soldurilor. Aplicația **nu calculează plafonul de încadrare ca microîntreprindere** și nu verifică dacă firma îl depășește: nu există în cod niciun modul care să citească veniturile din 765 și să le compare cu pragul de 100.000 euro din art. 47. Răspunsul de mai sus rămâne, deocamdată, o verificare pe care contabilul o face separat, din balanța de verificare.

[iConta.eu](/)
