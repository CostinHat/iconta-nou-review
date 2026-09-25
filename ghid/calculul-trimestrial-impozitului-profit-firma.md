---
title: "Cum fac calculul trimestrial al impozitului pe profit dacă firma are pierdere într-o lună?"
description: "De ce impozitul pe profit se calculează cumulat de la începutul anului fiscal, nu lună de lună, și ce se întâmplă când o lună din trimestru a adus pierdere."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum fac calculul trimestrial al impozitului pe profit dacă firma are pierdere într-o lună?

O firmă la impozit pe profit nu calculează separat impozitul pentru fiecare lună — legea cere calculul rezultatului fiscal cumulat, de la începutul anului fiscal. Dacă o lună din trimestru a adus pierdere, dar lunile anterioare sau următoare au adus profit, ceea ce contează la finalul trimestrului e rezultatul fiscal cumulat pe toată perioada, nu media sau suma lunilor calculate separat.

## Temeiul legal

::: ghid-temei
„(1) Rezultatul fiscal se calculează ca diferență între veniturile și cheltuielile înregistrate conform reglementărilor contabile aplicabile, din care se scad veniturile neimpozabile și deducerile fiscale și la care se adaugă cheltuielile nedeductibile. [...] Rezultatul fiscal pozitiv este profit impozabil, iar rezultatul fiscal negativ este pierdere fiscală. (2) Rezultatul fiscal se calculează trimestrial/anual, cumulat de la începutul anului fiscal."
— Legea nr. 227/2015 privind Codul fiscal, art. 19 alin. (1) și (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Consecința practică a calculului cumulat:

- **Impozitul datorat la un trimestru** se determină pe rezultatul fiscal cumulat de la 1 ianuarie până la sfârșitul trimestrului respectiv, nu pe rezultatul izolat al trimestrului sau al unei luni din el.
- **O pierdere dintr-o lună** nu generează, separat, o „reducere" de impozit sau o obligație negativă pentru luna respectivă — ea se compensează automat în calculul cumulat cu profitul altor luni din același an fiscal.
- **Impozitul de plată la un trimestru** rezultă ca diferență între impozitul calculat pe profitul cumulat până la finalul trimestrului curent și impozitul deja calculat/plătit pe profitul cumulat până la finalul trimestrului anterior — dacă profitul cumulat scade sub nivelul deja impozitat (de exemplu, din cauza unei pierderi semnificative într-o lună), diferența incrementală de plată e zero, nu negativă; regularizarea efectivă a eventualului surplus plătit se face prin declarația anuală (D101).

## Ce se greșește în practică

- Se calculează impozitul separat pentru fiecare lună/trimestru, ca și cum fiecare perioadă ar fi independentă — corect e calculul cumulat de la începutul anului, conform art. 19 alin. (2).
- Se presupune că o pierdere într-o lună „anulează" impozitul deja calculat și plătit pentru trimestrele anterioare, generând o restituire imediată — impozitul incremental al unui trimestru cu profit cumulat mai mic decât cel deja impozitat e zero de plată, nu negativ; eventuala regularizare finală se face abia prin declarația anuală.
- Se ignoră faptul că un trimestru cu profit, urmat de o lună cu pierdere mare, tot poate genera impozit de plată la trimestrul respectiv — ceea ce contează e rezultatul fiscal cumulat la finalul trimestrului, nu variația dintr-o singură lună.

## Ce face iConta.eu

iConta.eu calculează impozitul pe profit trimestrial exact pe baza logicii cumulate cerute de art. 19 alin. (2): în `core/d100.py`, baza efectivă a fiecărui trimestru se determină ca diferență între profitul cumulat de la 1 ianuarie până la sfârșitul trimestrului curent (plafonat la minimum zero) și profitul cumulat până la sfârșitul trimestrului anterior (plafonat la minimum zero) — mecanism care evită eroarea de a impozita integral, la cota de 16%, un trimestru cu profit venit imediat după un trimestru cu pierdere, și care dă corect zero de plată atunci când profitul cumulat scade sub nivelul deja impozitat anterior.

[iConta.eu](/)
