---
title: "Cum se calculează amortizarea fiscală liniară, degresivă și accelerată"
description: "Formulele și limitele legale ale celor trei regimuri de amortizare fiscală din Codul fiscal, cu regula de alegere pe categorie de mijloc fix."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează amortizarea fiscală liniară, degresivă și accelerată

Amortizarea fiscală nu e o singură formulă, ci trei regimuri diferite, iar legea nu lasă alegerea liberă pe orice mijloc fix: categoria activului decide ce metode sunt permise, iar coeficienții și plafoanele fiecărei metode sunt fixați prin lege, nu la latitudinea contabilului.

## Temeiul legal

::: ghid-temei
„(5) Regimul de amortizare pentru un mijloc fix amortizabil se determină conform următoarelor reguli: a) în cazul construcțiilor, se aplică metoda de amortizare liniară; b) în cazul echipamentelor tehnologice, respectiv al mașinilor, uneltelor și instalațiilor de lucru, precum și pentru computere și echipamente periferice ale acestora, contribuabilul poate opta pentru metoda de amortizare liniară, degresivă sau accelerată; c) în cazul oricărui altui mijloc fix amortizabil, contribuabilul poate opta pentru metoda de amortizare liniară sau degresivă.
(6) În cazul metodei de amortizare liniară, amortizarea se stabilește prin aplicarea cotei de amortizare liniară la valoarea fiscală de la data intrării în patrimoniul contribuabilului a mijlocului fix amortizabil.
(7) În cazul metodei de amortizare degresivă, amortizarea se calculează prin multiplicarea cotelor de amortizare liniară cu unul dintre coeficienții următori: a) 1,5, dacă durata normală de utilizare a mijlocului fix amortizabil este între 2 și 5 ani; b) 2,0, dacă durata normală de utilizare a mijlocului fix amortizabil este între 6 și 10 ani; c) 2,5, dacă durata normală de utilizare a mijlocului fix amortizabil este mai mare de 10 ani.
(8) În cazul metodei de amortizare accelerată, amortizarea se calculează după cum urmează: a) pentru primul an de utilizare, amortizarea nu poate depăși 50% din valoarea fiscală de la data intrării în patrimoniul contribuabilului a mijlocului fix; b) pentru următorii ani de utilizare, amortizarea se calculează prin raportarea valorii rămase de amortizare a mijlocului fix la durata normală de utilizare rămasă a acestuia.
(12) Amortizarea fiscală se calculează după cum urmează: a) începând cu luna următoare celei în care mijlocul fix amortizabil se pune în funcțiune, prin aplicarea regimului de amortizare prevăzut la alin. (5)."
— Legea 227/2015 (Codul fiscal), art. 28 alin. (5), (6), (7), (8), (12) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din text rezultă mecanica fiecărei metode:

- **Liniară** — cota anuală constantă (100% / durata normală de utilizare, în ani) aplicată la valoarea fiscală de intrare. Singura metodă permisă pentru construcții (alin. 5 lit. a) și singura mereu disponibilă, indiferent de categorie.
- **Degresivă** — cota liniară înmulțită cu un coeficient legal, fix pe trepte de durată: **1,5** (2-5 ani), **2,0** (6-10 ani), **2,5** (peste 10 ani). Nu se alege un coeficient „aproximativ" — treapta e dată de durata normală de utilizare stabilită la intrare.
- **Accelerată** — primul an: maximum 50% din valoarea fiscală de intrare; anii următori: valoarea rămasă de amortizat împărțită la durata rămasă. Disponibilă doar pentru echipamente tehnologice, mașini, unelte, instalații de lucru și computere (alin. 5 lit. b).
- **Momentul de start** — indiferent de metodă, amortizarea începe din **luna următoare** celei în care mijlocul fix e pus în funcțiune (alin. 12 lit. a), niciodată din luna achiziției sau a facturii.

Pentru anul 2026 există și o a patra metodă, temporară: amortizarea **superaccelerată** (plafon 65% în primul an), aplicabilă doar activelor noi din subgrupele 2.1 (echipamente tehnologice) și 2.4 (animale și plantații), puse în funcțiune între 1 ianuarie și 31 decembrie 2026 (CF art. 28 alin. (8^1), introdus de OUG 8/2026 art. 6 pct. 8).

## Ce se greșește în practică

- Se alege metoda degresivă sau accelerată pentru o construcție sau pentru un mijloc fix din categoria „orice alt mijloc fix" — legea permite degresivă doar acolo unde alin. (5) o prevede explicit, iar accelerata doar pentru echipamente/computere.
- Se folosește un coeficient degresiv „rotunjit" în loc de treapta exactă din alin. (7), sau se schimbă coeficientul pe parcurs quando durata rămasă trece dintr-o treaptă în alta — coeficientul se fixează la intrare, pe durata stabilită atunci.
- Se pornește amortizarea din luna facturii sau a plății, nu din luna următoare punerii în funcțiune.
- Se confundă amortizarea superaccelerată (excepție temporară 2026, doar echipamente tehnologice/animale și plantații noi) cu accelerata obișnuită, care nu are limită de an sau de subgrupă.

## Ce face iConta.eu

Motorul de amortizare din `core/d406_active.py` implementează toate patru metodele (liniară, degresivă, accelerată, superaccelerată) exact pe regulile de mai sus: coeficienții degresivi 1,5/2,0/2,5 pe treptele de durată, plafonul de 50% pentru accelerată în primul an (65% pentru superaccelerată), comutarea automată liniar↔degresiv quando liniarul devine mai avantajos, și restricțiile de categorie din CF art. 28 alin. (5) — pentru conturi de construcții (212) se permite doar liniară, pentru echipamente (2131) se adaugă accelerata, pentru animale/plantații (2134/217) superaccelerata doar dacă activul a fost pus în funcțiune în 2026. Dacă se cere o metodă nepermisă pentru categoria activului, motorul refuză explicit calculul, cu eroare care numește activul, contul, categoria și motivul — nu calculează tacit pe liniar.

Acest motor unic alimentează patru ecrane din aplicație: fișa mijlocului fix, nota lunară de amortizare, casarea și reevaluarea unui activ — deci cifrele de amortizare afișate în oricare din ele sunt consistente între ele, calculate de aceeași logică.

[iConta.eu](/)
