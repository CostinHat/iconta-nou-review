---
title: "TVA pentru aur și metale prețioase: regim special"
description: "Regimul special de TVA din art. 313 se aplică exclusiv aurului de investiții, nu metalelor prețioase în general — și ce anume implementează iConta.eu din el."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# TVA pentru aur și metale prețioase: regim special

Regimul special de TVA pentru aurul de investiții, prevăzut de art. 313 din Codul fiscal, e adesea generalizat greșit la „metale prețioase" — argint, platină sau alte metale. Legea, însă, reglementează **exclusiv aurul**, definit strict prin formă, puritate și, pentru monede, o serie de condiții suplimentare. Niciun alt metal prețios nu beneficiază de acest regim.

## Temeiul legal

::: ghid-temei
„a) aurul, sub formă de lingouri sau plachete acceptate/cotate pe piețele de metale prețioase, având puritatea minimă de 995 la mie, reprezentate sau nu prin hârtii de valoare, cu excepția lingourilor sau plachetelor cu greutatea de cel mult 1 g;
b) monedele de aur care îndeplinesc cumulativ următoarele condiții: 1. au titlul mai mare sau egal cu 900 la mie; 2. sunt reconfecționate după anul 1800; 3. sunt sau au constituit monedă legală de schimb în statul de origine; și 4. sunt vândute în mod normal la un preț care nu depășește valoarea de piață liberă a aurului conținut de monede cu mai mult de 80%."
— Codul fiscal (Legea 227/2015), art. 313 alin. (1) lit. a) și b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din text rezultă cu claritate perimetrul regimului:

- **Lingouri/plachete**: puritate minimă 995‰, cu o excepție importantă — lingourile sau plachetele de cel mult 1 gram **sunt excluse** din regim, chiar dacă au puritatea cerută.
- **Monede**: patru condiții cumulative (titlu ≥900‰, reconfecționate după 1800, au fost sau sunt monedă legală de schimb, preț de vânzare ≤ valoarea aurului conținut +80%).
- Niciun alt metal (argint, platină, paladiu) nu intră sub incidența art. 313 — regimul special (scutire de TVA, cu opțiune de taxare) se aplică **exclusiv** obiectelor din aur care îndeplinesc aceste condiții.

Livrarea aurului de investiții e, în principiu, **scutită de taxă** (art. 313 alin. (3)), cu posibilitatea ca vânzătorul care produce sau transformă aur de investiții să opteze pentru taxare — caz în care, către o altă persoană impozabilă, se aplică taxare inversă (art. 331 alin. (2) lit. h)).

## Ce se greșește în practică

- Se aplică scutirea de TVA specifică aurului și la vânzarea de argint sau alte metale prețioase, deși legea nu prevede acest regim decât pentru aur.
- Se ignoră excepția lingourilor/plachetelor de cel mult 1 gram — un lingou mic, deși are puritatea cerută, nu e „aur de investiții" în sensul legii și trebuie taxat normal.
- Se confundă condițiile pentru lingouri/plachete (doar puritate) cu cele pentru monede (patru condiții cumulative, inclusiv anul emisiunii și pragul de preț) — sunt seturi de reguli diferite.

## Ce face iConta.eu

iConta.eu are un ecran dedicat vânzării de „Aur de investiții (art. 313)", care calculează corect scutirea/taxarea inversă conform legii — dar, spus onest, cu limitele lui:

- Aplicația nu are un câmp de greutate pentru lingouri/plachete, deci nu verifică excepția „sub 1 gram" — un lingou mic ar putea fi clasificat greșit ca aur de investiții.
- Formularul de vânzare nu colectează anul emisiunii, prețul unitar sau valoarea aurului pentru opțiunea „Monedă" — condiții cerute explicit de motorul de calcul, deci vânzarea unei monede prin ecranul dedicat nu poate fi finalizată azi.
- Opțiunea de taxare inversă (către altă persoană impozabilă) nu are un câmp în formularul de vânzare, deși e testată corect la nivel de motor — nu poate fi declanșată încă dintr-o operațiune reală introdusă din interfață.

Regimul se aplică, în iConta.eu, **exclusiv** aurului — nu există, și nu ar trebui folosit, pentru vânzarea altor metale prețioase.

[iConta.eu](/)
