---
title: "Când sunt dobânzile deductibile integral?"
description: "Regula limitării deductibilității costurilor excedentare ale îndatorării la impozitul pe profit și situațiile în care dobânzile rămân deductibile integral."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Când sunt dobânzile deductibile integral?

Regula generală din Codul fiscal nu este „dobânda e deductibilă dacă e legată de activitate" — e o regulă de plafon, gândită să limiteze îndatorarea excesivă. Dar plafonul e suficient de generos încât majoritatea firmelor mici nici nu-l ating.

## Temeiul legal

::: ghid-temei
„Contribuabilul are dreptul de a deduce, într-o perioadă fiscală, costurile excedentare ale îndatorării până la plafonul deductibil reprezentat de echivalentul în lei al sumei de 1.000.000 euro. [...]
(5) Prin excepție de la alin. (1) și (4), în cazul în care contribuabilul este o entitate independentă, în sensul că nu face parte dintr-un grup consolidat în scopuri de contabilitate financiară, și nu are nicio întreprindere asociată și niciun sediu permanent, acesta deduce integral costurile excedentare ale îndatorării, în perioada fiscală în care acestea sunt suportate."
— Legea nr. 227/2015 (Codul fiscal), art. 40^2 alin. (4) și (5) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din text rezultă două căi spre deductibilitate integrală:

- **Plafonul de 1.000.000 euro**: costurile excedentare ale îndatorării (dobânda care depășește veniturile din dobânzi) sunt deductibile integral până la acest nivel anual; peste el, deducerea se limitează la 30% dintr-o bază de calcul specifică (EBITDA fiscal).
- **Entitatea independentă**: dacă firma nu face parte dintr-un grup consolidat, nu are întreprinderi asociate și nu are sediu permanent, deduce integral costurile îndatorării, indiferent de sumă — regula de plafon nu i se aplică deloc.
- Pentru tranzacțiile cu persoane afiliate, plafonul separat este de 500.000 euro, cu o limită totală combinată de 1.000.000 euro.

## Ce se greșește în practică

- Se aplică regula de plafon și firmelor mici, independente, fără să se verifice dacă se încadrează la excepția de „entitate independentă" de la alin. (5), care le-ar scuti complet de limitare.
- Se ignoră faptul că „costurile îndatorării" includ mai mult decât dobânda bancară clasică — și costul de finanțare al leasingului financiar, comisioane de intermediere, diferențe de curs la împrumuturi.
- Se calculează plafonul în lei fără să se folosească cursul de schimb comunicat de BNR pentru ultima zi a trimestrului/anului fiscal, așa cum cere legea.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează impozitul pe profit din datele contabile introduse (`core/d101.py`, `core/d100.py`), dar **nu automatizează testul de la art. 40^2** — nici verificarea plafonului de 1.000.000 euro, nici încadrarea firmei ca „entitate independentă", nici calculul bazei de 30% EBITDA fiscal. Ajustarea fiscală pentru costurile excedentare ale îndatorării rămâne o evaluare pe care contabilul o face manual și o introduce ca atare în calculul rezultatului fiscal.

[iConta.eu](/)
