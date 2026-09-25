---
title: "Greșeli la diferențe de curs: nerecunoscute la timp"
description: "De ce amânarea recunoașterii diferențelor de curs valutar e o greșeală contabilă frecventă și cum arată consecința ei în bilanț."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Greșeli la diferențe de curs: nerecunoscute la timp

Cea mai frecventă greșeală la diferențele de curs valutar nu e formula de calcul — e momentul. Legea cere recunoașterea diferenței exact în luna în care apare, fie la decontare, fie la reevaluarea lunară. Amânarea ei „pentru mai târziu" sau „pentru închiderea anului" denaturează rezultatul fiecărei luni intermediare.

## Temeiul legal

::: ghid-temei
„322. - (1) Diferențele de curs valutar care apar cu ocazia decontării creanțelor și datoriilor în valută la cursuri diferite față de cele la care au fost înregistrate inițial pe parcursul lunii sau față de cele la care sunt înregistrate în contabilitate trebuie recunoscute în luna în care apar, ca venituri sau cheltuieli din diferențe de curs valutar."
— OMFP 1802/2014, pct. 322 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- „Trebuie recunoscute în luna în care apar" e o obligație, nu o recomandare — nu există opțiunea de a le reporta pe o lună viitoare pentru simplitate.
- Reevaluarea lunară a soldurilor (pct. 325) e complementară: chiar dacă o creanță/datorie nu se decontează în luna respectivă, diferența de curs tot trebuie recunoscută lunar, pe baza cursului BNR din ultima zi bancară.
- Amânarea recunoașterii produce un efect dublu greșit: luna în care ar fi trebuit recunoscută iese cu rezultat denaturat (mai mic sau mai mare decât real), iar luna în care se recunoaște efectiv (întârziat) preia o sumă care nu-i aparține.
- Diferența întârziată, descoperită ulterior, se corectează potrivit regulilor de corectare a erorilor contabile — pe rezultatul reportat (cu declarație rectificativă) sau pe contul de profit și pierdere curent, în funcție de natura erorii.

## Ce se greșește în practică

- Se lasă notele de decontare valutară „pentru sfârșitul lunii" sau „pentru sfârșitul trimestrului", în loc să se înregistreze diferența odată cu decontarea efectivă.
- Se omite complet reevaluarea lunară a soldurilor nedecontate, considerând că diferența „oricum se va vedea la decontare" — greșit, pentru că reevaluarea lunară e o obligație separată, indiferent dacă soldul se decontează sau nu în acea lună.
- Se recunosc mai multe luni de diferențe cumulat, o singură dată, la sfârșitul trimestrului — practică ce ascunde exact volatilitatea pe care regula lunară vrea s-o reflecte corect.

## Ce face iConta.eu

Ambele operațiuni relevante din iConta.eu — decontarea (`core/uc_tenants.py: decontare_valuta`) și reevaluarea lunară (`reevaluare_valuta`) — generează nota contabilă în chiar luna operațiunii, cu data cerută de utilizator, respectând momentul de recunoaștere cerut de pct. 322. Ce **nu automatizează** aplicația este verificarea că, de fapt, contabilul a rulat reevaluarea în fiecare lună la timp: dacă o lună a fost închisă fără reevaluare, aplicația nu emite niciun avertisment proactiv — constrângerea `_cere_luna_deschisa` doar blochează încercarea de a mai scrie retroactiv într-o lună închisă, nu semnalează omisiunea în avans.

[iConta.eu](/)
