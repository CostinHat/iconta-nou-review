---
title: "Comisioanele intră în costul de achiziție al unui mijloc fix?"
description: "Ce spune OMFP 1802/2014 despre includerea comisioanelor atribuibile direct achiziției în costul de intrare al unui mijloc fix, și de ce iConta.eu nu repartizează automat aceste costuri decât pentru stocuri, nu și pentru mijloace fixe."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Comisioanele intră în costul de achiziție al unui mijloc fix?

Definiția „costului de achiziție" din reglementările contabile românești e una singură, folosită atât pentru stocuri, cât și pentru mijloacele fixe — nu există o definiție separată, mai restrictivă, pentru imobilizările corporale. Prin urmare, comisioanele legate direct de achiziția unui mijloc fix (de exemplu comisionul unui intermediar/broker la cumpărarea unui utilaj) intră, ca regulă, în costul lui de intrare.

## Temeiul legal

::: ghid-temei
„6. cost de achiziție înseamnă prețul datorat și eventualele cheltuieli conexe minus eventualele reduceri ale costului de achiziție. În acest sens, costul de achiziție al bunurilor cuprinde prețul de cumpărare, taxele de import și alte taxe (cu excepția acelora pe care persoana juridică le poate recupera de la autoritățile fiscale), cheltuielile de transport, manipulare și alte cheltuieli care pot fi atribuibile direct achiziției bunurilor respective. În costul de achiziție se includ, de asemenea, comisioanele, taxele notariale, cheltuielile cu obținerea de autorizații și alte cheltuieli nerecuperabile, atribuibile direct bunurilor respective. [...]"
— OMFP 1802/2014, Secțiunea 1.2, pct. 6 (sursă: anaf_surse/omfp_1802_2014.txt)
:::

Faptul că această definiție se aplică și mijloacelor fixe, nu doar stocurilor, rezultă din regula generală de evaluare la intrare, aplicabilă tuturor „bunurilor":

::: ghid-temei
„75. - (1) La data intrării în entitate, bunurile se evaluează și se înregistrează în contabilitate la valoarea de intrare, care se stabilește astfel: a) la cost de achiziție - pentru bunurile procurate cu titlu oneros; [...]"
— OMFP 1802/2014, Capitolul 3 „Reguli generale de evaluare", Secțiunea 3.1, pct. 75 alin. (1) (sursă: anaf_surse/omfp_1802_2014.txt)
:::

Deci: dacă un comision e **atribuibil direct** achiziției unui mijloc fix concret (comision de intermediere, comision de broker vamal la o achiziție din import), el se capitalizează în valoarea de intrare a activului. Nu se includ, în schimb, comisioanele de natura costurilor de finanțare (comision de acordare/administrare a unui credit folosit pentru achiziție) — acelea urmează regimul distinct al costurilor îndatorării (pct. 79-80 din același ordin), capitalizabile doar pentru active cu ciclu lung de fabricație, categorie din care un mijloc fix cumpărat gata de utilizare e explicit exclus.

## Ce se greșește în practică

- Se include în costul mijlocului fix orice comision plătit „în legătură cu" achiziția, indiferent dacă e unul de intermediere directă a bunului sau unul de finanțare (dobândă/comision de credit) — doar primul se capitalizează.
- Se presupune că regula de capitalizare a costurilor accesorii (transport, comisioane) există doar pentru mărfuri/stocuri — definiția din pct. 6 și regula de evaluare din pct. 75 sunt generice, valabile și pentru imobilizări corporale.
- Se lasă comisionul pe cheltuieli de exploatare ale perioadei, direct, fără verificarea condiției de atribuire directă la un activ identificabil.

## Ce face iConta.eu

Mecanismul automat de capitalizare a costurilor accesorii (transport, taxe) pe articolele unei intrări în gestiune — **F139, Landed cost pe NIR** (`core/stocuri.py::nir_gv`) — e construit exclusiv pentru **stocuri**, pe metoda global-valorică (F088). Verificat explicit în cod: motorul de gestiune cantitativ-valorică (CMP) nu are niciun parametru de accesoriu, iar modulul de import/migrare a mijloacelor fixe (F059, `core/mijloace_fixe_import_api.py`) preia direct valoarea de intrare introdusă de contabil, fără o funcție de repartizare proporțională a unor costuri accesorii pe mai multe active.

Practic, deși temeiul legal (OMFP 1802/2014, pct. 6) susține includerea unui comision direct atribuibil în costul de achiziție al unui mijloc fix, **iConta.eu nu are un mecanism automat care să facă această capitalizare pentru mijloace fixe** — contabilul introduce el însuși valoarea de intrare completă (preț + comision atribuibil), fie la înregistrarea inițială a activului, fie la migrarea registrului dintr-un alt program.

[iConta.eu](/)
