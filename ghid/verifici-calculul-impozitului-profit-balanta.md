---
title: "Cum verifici calculul impozitului pe profit din balanță?"
description: "Formula legală a rezultatului fiscal și cota de impozitare, pentru a verifica din balanța de verificare dacă impozitul pe profit e calculat corect."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verifici calculul impozitului pe profit din balanță?

Impozitul pe profit nu se calculează direct din rezultatul contabil (contul de profit și pierdere) — trece printr-un rezultat fiscal, obținut prin ajustarea rezultatului contabil cu elemente specifice legii fiscale. Verificarea din balanță pornește exact de la această formulă.

## Temeiul legal

::: ghid-temei
„Rezultatul fiscal se calculează ca diferență între veniturile și cheltuielile înregistrate conform reglementărilor contabile aplicabile, din care se scad veniturile neimpozabile și deducerile fiscale și la care se adaugă cheltuielile nedeductibile. La stabilirea rezultatului fiscal se iau în calcul și elemente similare veniturilor și cheltuielilor, potrivit normelor metodologice, precum și pierderile fiscale care se recuperează în conformitate cu prevederile art. 31."

„Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."
— Codul fiscal, art. 19 alin. (1) și art. 17 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Traducerea în pași de verificare, plecând din balanța de verificare:

1. **Rezultatul contabil** = total conturi de venituri (clasa 7) − total conturi de cheltuieli (clasa 6), preluat din rulajele balanței.
2. **Se scad veniturile neimpozabile** (de ex. dividende primite deja impozitate, venituri din anularea unor provizioane nedeductibile la constituire) — identificabile din analiticele conturilor de venituri.
3. **Se adaugă cheltuielile nedeductibile** (protocol/sponsorizări peste plafon, amenzi, cheltuieli nejustificate prin documente) — identificabile din analiticele conturilor de cheltuieli marcate ca atare.
4. **Se scad deducerile fiscale suplimentare** (dacă e cazul) și se recuperează pierderea fiscală reportată din anii anteriori.
5. Asupra rezultatului astfel obținut (profitul impozabil) se aplică **cota de 16%**.

Dacă suma din declarație nu se potrivește cu acest calcul refăcut din balanță, diferența e aproape mereu la pasul 2 sau 3 — o cheltuială nedeductibilă neadăugată sau un venit neimpozabil netratat corect.

## Ce se greșește în practică

- Se aplică 16% direct pe rezultatul contabil din balanță, fără ajustările cerute de art. 19 alin. (1) (venituri neimpozabile de la art. 23, cheltuieli nedeductibile de la art. 25) — corect doar dacă firma nu are niciun element de venit neimpozabil sau cheltuială nedeductibilă în perioada respectivă, ceea ce e rar.
- Se omite recuperarea pierderii fiscale din anii anteriori, deși legea o permite explicit ca element de scădere din rezultatul fiscal.
- Se confundă cheltuielile nedeductibile **integral** (ex. amenzi) cu cele deductibile **limitat** (protocol, sponsorizare, provizioane) — tratamentul și plafonul diferă, iar balanța singură nu arată automat această distincție fără analitice corect setate.

## Ce face iConta.eu

iConta.eu calculează impozitul pe profit direct din datele contabile introduse în aplicație (declarația D101), aplicând ajustările pentru veniturile neimpozabile și cheltuielile nedeductibile pe baza conturilor/analiticelor configurate. Verificarea manuală din balanță descrisă mai sus rămâne utilă ca probă de control încrucișat, independent de calculul automat al aplicației.

[iConta.eu](/)
