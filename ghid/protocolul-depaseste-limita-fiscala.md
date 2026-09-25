---
title: "Ce fac cu protocolul care depășește limita fiscală?"
description: "Cheltuielile de protocol au deductibilitate limitată la 2% dintr-o bază calculată pe profitul contabil — ce se întâmplă fiscal cu partea care trece de acest plafon."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac cu protocolul care depășește limita fiscală?

Cheltuielile de protocol (mese de afaceri, cadouri pentru parteneri etc.) nu sunt deductibile integral la calculul impozitului pe profit, ci doar până la un plafon de 2% aplicat unei baze specifice. Partea care depășește acest plafon rămâne cheltuială contabilă, dar devine nedeductibilă fiscal.

## Temeiul legal

::: ghid-temei
„Următoarele cheltuieli au deductibilitate limitată: a) cheltuielile de protocol în limita unei cote de 2% aplicată asupra profitului contabil la care se adaugă cheltuielile cu impozitul pe profit și cheltuielile de protocol. În cadrul cheltuielilor de protocol se includ și cheltuielile înregistrate cu taxa pe valoarea adăugată colectată potrivit prevederilor titlului VII, pentru cadourile oferite de contribuabil, cu valoare mai mare de 100 lei."
— Legea nr. 227/2015 (Codul fiscal), art. 25 alin. (3) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Plafonul de 2% **nu se aplică la cheltuiala de protocol în sine**, ci la o bază compusă: profitul contabil + cheltuiala cu impozitul pe profit + cheltuiala de protocol înregistrată.
- Verificarea depășirii plafonului se face **la finalul anului fiscal** (sau la închiderea trimestrului, pentru contribuabilii care plătesc trimestrial), pentru că baza de calcul depinde de rezultatul contabil cumulat.
- Partea din cheltuiala de protocol care depășește 2% din bază **rămâne cheltuială contabilă**, dar se adaugă înapoi la calculul rezultatului fiscal (element nedeductibil), majorând impozitul pe profit datorat.
- TVA colectată pentru cadourile de protocol cu valoare peste 100 lei se include, la rândul ei, în baza cheltuielii de protocol — nu se tratează separat.

## Ce se greșește în practică

- Se calculează plafonul de 2% direct din valoarea cheltuielii de protocol, în loc de baza compusă (profit contabil + impozit pe profit + protocol).
- Se face verificarea plafonului lunar sau trimestrial fără recalculare la sfârșitul anului, deși baza de calcul se modifică pe măsură ce se acumulează rezultatul contabil.
- Se omite includerea TVA colectată pentru cadourile peste 100 lei în valoarea cheltuielii de protocol, subestimând astfel suma supusă plafonării.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are contul 623 „Cheltuieli de protocol, reclamă și publicitate" mapat în planul de conturi (`core/plan_omfp.py`), astfel încât aceste cheltuieli pot fi înregistrate distinct în evidența contabilă. Nu am găsit însă, în modulul de impozit pe profit (`core/d101.py`), o funcție care să calculeze automat plafonul de 2% pe baza compusă (profit contabil + impozit pe profit + protocol) și să identifice partea nedeductibilă de reintrodus în calculul fiscal — acest calcul rămâne, la acest moment, în sarcina contabilului, pe baza rulajului contului 623.

[iConta.eu](/)
