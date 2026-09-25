---
title: "Diferențele de curs valutar intră în rezultatul fiscal?"
description: "Da, ca regulă generală — veniturile și cheltuielile din diferențe de curs urmează calculul standard al rezultatului fiscal, fără o excludere dedicată."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Diferențele de curs valutar intră în rezultatul fiscal?

Da. La impozitul pe profit, rezultatul fiscal pornește de la ce ai înregistrat contabil, iar diferențele de curs valutar (665/765) nu au o linie de excepție dedicată în Codul fiscal — deci intră în calcul exact cum au fost înregistrate: venit impozabil dacă e câștig, cheltuială deductibilă dacă e pierdere.

## Temeiul legal

::: ghid-temei
„(1) Rezultatul fiscal se calculează ca diferență între veniturile și cheltuielile înregistrate conform reglementărilor contabile aplicabile, din care se scad veniturile neimpozabile și deducerile fiscale și la care se adaugă cheltuielile nedeductibile. [...] Rezultatul fiscal pozitiv este profit impozabil, iar rezultatul fiscal negativ este pierdere fiscală."
— Legea 227/2015 (Codul fiscal), art. 19 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Formula legală pleacă de la rezultatul contabil (venituri minus cheltuieli, conform OMFP 1802/2014) și aplică doar două tipuri de corecții: scăderea veniturilor neimpozabile (art. 23) și adăugarea cheltuielilor nedeductibile (art. 25).
- Verificat: niciunul din articolele care listează venituri neimpozabile sau cheltuieli nedeductibile, aplicabile firmelor obișnuite (nu organizații nonprofit), nu menționează diferențele de curs valutar din activitatea comercială curentă.
- Singura zonă unde diferențele de curs primesc un tratament special e la costurile îndatorării — dobânzi și pierderi nete din curs asociate finanțării prin datorii, plafonate potrivit regulilor de la art. 40^2 (regim tip ATAD, aplicabil peste un anumit prag).
- Concluzia practică: în afara acestei excepții punctuale, un venit din 765 mărește profitul impozabil, o cheltuială din 665 îl micșorează — fără plafonare, fără reportare specială.

## Ce se greșește în practică

- Se caută în mod repetat o excludere generală pentru diferențele de curs, presupunând că „sunt doar contabile, nu fiscale" — presupunere greșită în lipsa unei norme care să le excludă.
- Se aplică plafonarea de la costurile îndatorării (art. 40^2) și diferențelor de curs din facturi comerciale obișnuite, care nu au legătură cu finanțarea prin datorii.
- Se ignoră regimul diferit de la microîntreprinderi (art. 53), unde diferențele de curs chiar sunt scoase din baza impozabilă lunară, aplicând greșit regula de la impozit pe profit.

## Ce face iConta.eu

`core/diferente_curs.py` calculează și contabilizează diferențele de curs (665/765), dar aplicația **nu calculează rezultatul fiscal** și nu aplică art. 19-40^2 asupra acestor sume — modulul e, cum spune el însuși, un „motor pur", fără nicio legătură de cod cu declarația de impozit pe profit. Sumele generate automat de F041 alimentează balanța de verificare, de unde contabilul le preia manual în calculul rezultatului fiscal.

[iConta.eu](/)
