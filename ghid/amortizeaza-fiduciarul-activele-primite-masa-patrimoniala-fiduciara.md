---
title: "Cum amortizează fiduciarul activele primite în masa patrimonială fiduciară?"
description: "Fiduciarul preia activele la valoarea fiscală de la constituitor și continuă amortizarea fiscală după regulile care s-ar fi aplicat constituitorului, ca și cum transferul nu ar fi avut loc."
published: 2026-10-02
modified: 2026-10-03
poarta: v1
---

# Cum amortizează fiduciarul activele primite în masa patrimonială fiduciară?

Fiduciarul **nu reîncepe amortizarea**. Când constituitorul este și beneficiarul fiduciei, activele intră în masa patrimonială fiduciară cu **aceeași valoare fiscală** pe care o aveau la constituitor. Amortizarea fiscală se determină **în continuare după regulile care s-ar fi aplicat constituitorului**, ca și cum transferul nu ar fi avut loc: aceeași metodă, aceeași valoare și aceeași durată, din punctul în care s-a oprit.

Practic, transferul în fiducie nu e un prilej de reevaluare fiscală, de schimbare a metodei sau de reluare a duratei de amortizare.

## Temeiul legal

::: ghid-temei
„valoarea fiscală a activelor cuprinse în masa patrimonială fiduciară, preluată de fiduciar, este egală cu valoarea fiscală pe care acestea au avut-o la constituitor"
— Codul fiscal (Legea 227/2015), art. 30 alin. (1) lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„amortizarea fiscală pentru orice activ amortizabil prevăzut în masa patrimonială fiduciară se determină în continuare în conformitate cu regulile prevăzute la art. 28 , care s-ar fi aplicat la persoana care a transferat activul, dacă transferul nu ar fi avut loc."
— Codul fiscal (Legea 227/2015), art. 30 alin. (1) lit. d) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

::: ghid-temei
„fiduciarul va conduce o evidență contabilă separată pentru masa patrimonială fiduciară și va transmite trimestrial către constituitor, pe bază de decont, veniturile și cheltuielile rezultate din administrarea patrimoniului conform contractului"
— Codul fiscal (Legea 227/2015), art. 30 alin. (1) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă pentru fiduciar și pentru constituitor:

- **Valoarea de pornire** este valoarea fiscală de la constituitor, nu valoarea de piață și nici prețul din contract (lit. c)).
- **Regulile rămân cele ale constituitorului** (lit. d)). Se păstrează metoda aleasă de constituitor (liniară, degresivă sau accelerată, după caz), durata normală de utilizare și amortizarea deja dedusă. Fiduciarul continuă calculul pentru durata rămasă.
- **Fără opțiune nouă de metodă.** Formula „dacă transferul nu ar fi avut loc" exclude, în lectura firească, alegerea unei metode noi doar pentru că activul a ajuns la fiduciar.
- **Unde ajunge cheltuiala cu amortizarea.** Fiduciarul ține o evidență separată pentru masa fiduciară și transmite trimestrial constituitorului, prin decont, veniturile și cheltuielile din administrare (lit. b)). Amortizarea calculată pe regulile de mai sus intră, ca orice cheltuială de administrare, în decontul către constituitor, care e și beneficiar. Legea nu detaliază mecanica decontului pe fiecare element, așa că modul de reflectare se stabilește prin contract și politici contabile.
- **Când nu se aplică.** Dacă beneficiarul fiduciei este fiduciarul sau un terț, art. 30 alin. (1) nu se aplică. Constituitorul are atunci cheltuieli nedeductibile din transfer (art. 30 alin. (2)), iar continuitatea amortizării nu mai e garantată de acest articol.

::: ghid-exemplu
SC Exemplu SRL (constituitor și beneficiar) transferă în fiducie, la 1 ianuarie 2026, un utilaj cu valoarea fiscală de 500.000 lei. Utilajul se amortizează liniar pe o durată normală de 10 ani și a fost pus în funcțiune la 1 ianuarie 2022. Până la transfer s-au dedus 4 ani × 50.000 = 200.000 lei.

- Valoarea fiscală la fiduciar: 500.000 lei (lit. c)).
- Amortizare rămasă: 500.000 − 200.000 = 300.000 lei, pe 6 ani.
- Amortizare anuală continuată: 300.000 / 6 = 50.000 lei, aceeași ca înainte de transfer.
- În fiecare trimestru din 2026, amortizarea de 12.500 lei intră în decontul transmis de fiduciar către SC Exemplu SRL, alături de veniturile și celelalte cheltuieli ale masei fiduciare.

Ar fi greșit ca fiduciarul să amortizeze utilajul pe 10 ani noi, la o valoare de piață de 450.000 lei.
:::

## Ce se greșește în practică

- Fiduciarul înregistrează activul la valoarea de piață și reia amortizarea pe o durată întreagă.
- Fiduciarul schimbă metoda de amortizare, de exemplu din liniară în accelerată, deși legea cere regulile constituitorului.
- Amortizarea e dedusă de două ori: de fiduciar în evidența lui și de constituitor prin decont.
- Nu se transmite istoricul fiscal al activelor (valoare fiscală, amortizare deja dedusă, metodă, durată), fără de care fiduciarul nu poate continua corect calculul.
- Regula se aplică și fiduciilor în favoarea unui terț, unde art. 30 alin. (1) nu e aplicabil.

## Ce face iConta.eu

Registrul de mijloace fixe din iConta.eu calculează amortizarea la zi pe metoda fiecărui activ (liniară, degresivă, accelerată sau superaccelerată), pornind de la data punerii în funcțiune. La preluarea activelor dintr-un registru exportat din alt program, aplicația amortizează valoarea de intrare pe toată durata, din data punerii în funcțiune; coloana „valoare rămasă” din fișier servește doar ca verificare și dă avertisment dacă nu se leagă cu calculul. Aplicația nu are un modul dedicat masei patrimoniale fiduciare și nu generează decontul trimestrial al fiduciarului, care rămâne în sarcina contabilului.

[iConta.eu](/)
