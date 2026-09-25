---
title: "Eroare frecventă: plafonul micro calculat pe venituri contabile"
description: "De ce plafonul de 100.000 euro pentru încadrarea ca microîntreprindere se verifică pe cifra de afaceri, nu pe totalul veniturilor contabile din clasa 7."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Eroare frecventă: plafonul micro calculat pe venituri contabile

Una dintre confuziile care apar constant la finalul anului este verificarea plafonului de 100.000 euro pentru microîntreprinderi pe baza rulajului total al conturilor de venituri (clasa 7), în loc de cifra de afaceri, așa cum cere efectiv legea. Diferența poate fi decisivă acolo unde firma are și venituri financiare sau extraordinare semnificative.

## Temeiul legal

```
::: ghid-temei
„Pentru încadrarea în condițiile privind nivelul veniturilor prevăzute la art. 47 alin. (1) lit. c) și la art. 52 alin. (1) se iau în calcul veniturile care constituie cifra de afaceri definită potrivit reglementărilor contabile aplicabile."
— Legea nr. 227/2015 privind Codul fiscal, art. 54 alin. (1), astfel cum a fost modificat prin OUG nr. 8/2026, coroborat cu art. 47 alin. (1) lit. c) (sursă: anaf_surse/oug_8_2026.txt)
:::
```

Iar condiția de bază, la care se raportează acest calcul:

```
::: ghid-temei
„c) a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile."
— Legea nr. 227/2015 privind Codul fiscal, art. 47 alin. (1) lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::
```

Ce rezultă din coroborarea celor două texte:

- **Plafonul de 100.000 euro se verifică pe cifra de afaceri**, definită potrivit reglementărilor contabile — nu pe rulajul cumulat al tuturor conturilor de venituri (care ar include, de exemplu, venituri financiare din diferențe de curs, dobânzi, sau venituri din subvenții).
- **Cursul de schimb** folosit pentru echivalentul în euro e cel valabil la închiderea exercițiului financiar în care s-au înregistrat veniturile, nu cursul de la data fiecărei încasări în parte.
- Pentru anul fiscal 2026, verificarea condițiilor de încadrare ca microîntreprindere se face potrivit acestei reguli, aplicabilă explicit inclusiv pentru 2026, conform notei de aplicare din OUG nr. 8/2026.

## Ce se greșește în practică

- Se adună toate rulajele conturilor din clasa 7 (inclusiv 766 „Venituri din dobânzi", 765 „Venituri din diferențe de curs valutar", 758 „Alte venituri din exploatare" nelegate de activitatea de bază) și se compară totalul cu plafonul de 100.000 euro — deși legea cere strict cifra de afaceri.
- Se folosește un curs de schimb mediu anual sau cursul de la data fiecărei facturi, în loc de cursul BNR valabil la data închiderii exercițiului financiar.
- Se ignoră faptul că aceeași regulă a cifrei de afaceri (nu venituri totale) se aplică și la verificarea altor plafoane din același titlu, de exemplu la art. 52 alin. (1), referitor la ieșirea din sistemul micro în cursul anului.

## Ce face iConta.eu

iConta.eu calculează baza impozitului micro de 1% din veniturile din conturile 70x, 75x și 76x, minus reducerile comerciale 709 (`core/repo_d100.py`, motorul A8) — o bază conform art. 53, dar mai largă decât „cifra de afaceri" (doar grupa 70x) cerută de art. 54 alin. (1) pentru verificarea plafonului. La data acestui ghid, aplicația nu are un modul separat care să calculeze strict cifra de afaceri (grupa 70x, fără 75x/76x) și să verifice automat plafonul de 100.000 euro de la art. 47 alin. (1) lit. c) și art. 52 alin. (1) — folosirea bazei impozitului micro (70x+75x+76x) ca substitut pentru cifra de afaceri ar supraestima veniturile relevante pentru plafon; verificarea corectă, pe cifra de afaceri strictă, rămâne o operațiune manuală a contabilului.

[iConta.eu](/)
