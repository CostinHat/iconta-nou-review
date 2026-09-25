---
title: "Scutirea de impozit pentru ONG-uri: condiții"
description: "Un ONG e scutit de impozit pe profit doar pentru veniturile enumerate expres de lege și, pentru rest, doar sub un plafon dublu limitat — nu automat, pe toate veniturile."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Scutirea de impozit pentru ONG-uri: condiții

Nu există o scutire generală „ONG-urile nu plătesc impozit pe profit". Legea condiționează scutirea de natura fiecărui venit în parte: unele categorii sunt neimpozabile necondiționat, indiferent de sumă, iar restul veniturilor pot fi neimpozabile doar până la un plafon calculat pe două limite simultane.

## Temeiul legal

::: ghid-temei
„(2) În cazul organizațiilor nonprofit, organizațiilor sindicale, organizațiilor patronale, la calculul rezultatului fiscal, următoarele tipuri de venituri sunt venituri neimpozabile: a) cotizațiile și taxele de înscriere ale membrilor; b) contribuțiile bănești sau în natură ale membrilor și simpatizanților; c) taxele de înregistrare stabilite potrivit legislației în vigoare; [...] e) donațiile, precum și banii sau bunurile primite prin sponsorizare/mecenat; f) veniturile din dividende, dobânzi, precum și din diferențele de curs valutar aferente disponibilităților și veniturilor neimpozabile; [...] i) resursele obținute din fonduri publice sau din finanțări nerambursabile; j) veniturile realizate din acțiuni ocazionale precum: evenimente de strângere de fonduri cu taxă de participare, serbări, tombole, conferințe, utilizate în scop social sau profesional, potrivit statutului acestora; [...]
(3) [...] pentru calculul rezultatului fiscal sunt neimpozabile și alte venituri realizate, până la nivelul echivalentului în lei a 15.000 euro, într-un an fiscal, dar nu mai mult de 10% din veniturile totale neimpozabile prevăzute la alin. (2)."
— art. 15 alin. (2)-(3) din Legea 227/2015 (Codul fiscal) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Condițiile, pe scurt:

- **Prima condiție** — venitul să se încadreze într-una din categoriile enumerate expres la alin. (2): cotizații/taxe de înscriere, contribuții ale membrilor, donații/sponsorizare, dobânzi/diferențe de curs pe disponibilități neimpozabile, fonduri publice/finanțări nerambursabile, acțiuni ocazionale etc. Pentru acestea, scutirea e necondiționată de sumă.
- **A doua condiție**, pentru orice alt venit (tipic economic) — se aplică plafonul de la alin. (3): minimul dintre **15.000 EUR/an fiscal** și **10% din totalul veniturilor neimpozabile** de la alin. (2). Cele două limite se aplică **simultan**, nu alternativ — contează cea mai mică.
- Suma în lei a celor 15.000 EUR se calculează cu **cursul mediu de schimb valutar EUR/RON comunicat de BNR pentru anul fiscal respectiv**, nu cu cursul de la 31 decembrie — norma metodologică la art. 15 o precizează explicit:

::: ghid-temei
„(i) calculul sumei în lei reprezentând echivalentul a 15.000 euro prin utilizarea cursului mediu de schimb valutar EUR/RON comunicat de Banca Națională a României pentru anul fiscal respectiv;"
— HG 1/2016, norma la art. 15 pct. 3 lit. b) subpct. (i) din Codul fiscal (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

## Ce se greșește în practică

- Se calculează echivalentul în lei al celor 15.000 EUR la cursul BNR din 31 decembrie, în loc de **cursul mediu anual** — o eroare frecventă, întâlnită și în unele materiale de ajutor, care denaturează plafonul de scutire.
- Se aplică doar limita de 15.000 EUR, ignorând complet plafonul de 10% din veniturile neimpozabile — dacă organizația are venituri neimpozabile mici, plafonul real de scutire poate fi mult sub 15.000 EUR.
- Se presupune că orice venit al unui ONG e automat neimpozabil — condiția e ca venitul să se încadreze expres la alin. (2) sau, pentru rest, sub plafonul de la alin. (3); peste plafon, venitul economic e impozabil la cota standard.

## Ce face iConta.eu

Calculatorul din ecranul „Operațiuni ONG" compară cele două limite — 15.000 EUR la cursul introdus de utilizator și 10% din veniturile neimpozabile ale anului — și reține minimul dintre ele ca plafon de scutire, apoi estimează impozitul de 16% pe partea rămasă impozabilă. Calculul propriu-zis e corect ca formulă, dar **iConta.eu nu alege singur cursul valutar** — acesta trebuie introdus manual de utilizator, care trebuie să folosească explicit cursul mediu anual BNR, nu cursul de sfârșit de an, altfel plafonul iese greșit. De asemenea, acest calcul e accesibil azi doar printr-un apel API direct, nu din formularul afișat în ecranul „Operațiuni ONG".

[iConta.eu](/)
