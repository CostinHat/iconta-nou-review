---
title: "Cum se tratează facturile stornate la un PFA în sistem real?"
description: "De ce stornarea unei facturi la un PFA în sistem real depinde de faptul dacă suma a fost sau nu efectiv încasată, conform principiului de casă al venitului brut din Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se tratează facturile stornate la un PFA în sistem real?

Un PFA care conduce contabilitate în sistem real (partidă simplă) nu determină venitul pe bază de facturi emise, ci pe bază de **încasări și plăți efective** — registrul de evidență fiscală e, prin natura lui, un registru de casă. Această particularitate schimbă radical modul în care se tratează o factură stornată: efectul stornării depinde de faptul dacă banii au fost sau nu încasați înainte de stornare.

## Temeiul legal

::: ghid-temei
„(1) Venitul net anual din activități independente se determină în sistem real, pe baza datelor din contabilitate, ca diferență între venitul brut și cheltuielile deductibile efectuate în scopul realizării de venituri [...]
(2) Venitul brut cuprinde: a) sumele încasate și echivalentul în lei al veniturilor în natură din desfășurarea activității; [...]"
— Codul fiscal (Legea 227/2015), art. 68 alin. (1) și alin. (2) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din text rezultă principiul de bază: venitul brut al unui PFA în sistem real nu e „ce s-a facturat", ci strict **sumele încasate**. Consecința directă pentru facturile stornate:

- **Factură emisă, dar neîncasată încă, apoi stornată** — nu are niciun impact fiscal, pentru că suma nu a intrat niciodată în venitul brut (nu a fost încasată). Stornarea e, în acest caz, o simplă corecție a evidenței comerciale, fără efect asupra registrului de încasări și plăți.
- **Factură deja încasată, apoi stornată cu restituirea banilor către client** — restituirea efectivă e o **plată**, care se înregistrează la data la care are loc efectiv, nu retroactiv la data facturii inițiale. Ea reduce venitul brut al perioadei în care se face restituirea, nu al perioadei în care fusese emisă factura originală — pentru că sistemul e pe bază de casă, nu de angajamente.

## Ce se greșește în practică

- Se „scade" suma stornată din venitul lunii facturii inițiale, ca într-o contabilitate de angajamente — greșit pentru sistemul real al PFA, care e strict pe încasări/plăți efective la data lor reală.
- Se lasă suma stornată neînregistrată dacă restituirea a avut loc efectiv, doar pentru că factura originală „nu mai există" — restituirea e o operațiune de sine stătătoare (o plată), care trebuie înregistrată la data ei.
- Se confundă o factură stornată-neîncasată (fără efect fiscal) cu una stornată-după-încasare (cu efect fiscal, la data restituirii) — distincția depinde exclusiv de faptul dacă banii intraseră deja în cont sau în casă.

## Ce face iConta.eu

Motorul de calcul al Fișei D212 pentru PFA în sistem real (F030, `core/d212_engine.py` + `core/rip_api.fisa_d212`) citește exclusiv operațiunile **validate** din registrul de încasări și plăți (RIP): venitul brut e suma încasărilor cu categoria „activitate", iar cheltuielile deductibile sunt suma plăților cu categoria corespunzătoare — coerent cu principiul de casă din art. 68 alin. (2) lit. a) de mai sus. Operațiunile lăsate ca ciornă, nevalidate, nu intră în calcul, dar sunt semnalate separat ca „ciorne nevalidate", tocmai ca să nu fie pierdute din calculul final fără ca cineva să observe.

Aplicația **nu are un mecanism dedicat de „storno" al unei operațiuni din RIP** — verificat în cod, motorul citește doar suma operațiunilor validate, pe categorie, fără o funcție separată de anulare/reversare. Practic, tratamentul descris mai sus (o încasare neefectuată nu intră niciodată în calcul; o restituire efectivă se înregistrează ca operațiune de plată distinctă, la data ei reală, în categoria corespunzătoare) se aplică natural prin felul în care contabilul introduce operațiunile reale în RIP, nu printr-o funcție specială de stornare a aplicației.

[iConta.eu](/)
