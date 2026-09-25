---
title: "Ce faci dacă amortizarea nu a fost calculată timp de câteva luni?"
description: "Cum se corectează o amortizare fiscală omisă pe câteva luni, fără a pierde dreptul de deducere, potrivit regulilor Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce faci dacă amortizarea nu a fost calculată timp de câteva luni?

Dacă se descoperă că amortizarea unui mijloc fix nu a fost calculată pentru câteva luni (de regulă din cauza unei erori de configurare sau a unei omisiuni la punerea în funcțiune), cheltuiala cu amortizarea aferentă acelor luni nu dispare — se corectează, iar tratamentul depinde de momentul la care se descoperă eroarea: în cursul aceluiași an fiscal sau după închiderea lui.

## Temeiul legal

::: ghid-temei
„Amortizarea fiscală se calculează după cum urmează: a) începând cu luna următoare celei în care mijlocul fix amortizabil se pune în funcțiune, prin aplicarea regimului de amortizare prevăzut la alin. (5) [...]"
— Legea 227/2015, art. 28 alin. (12) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce se face concret, în funcție de moment:

- **Dacă eroarea se descoperă în același an fiscal** (de exemplu, luni omise în trimestrul curent, neînchis încă declarativ) — se recalculează amortizarea lunilor omise și se include în cheltuiala deductibilă a lunii curente sau a lunii în care se face corecția, cu explicarea în notele contabile a motivului.
- **Dacă eroarea privește o perioadă din anii fiscali anteriori, deja declarați** — corectarea nu se face prin simpla „recuperare" a amortizării omise în luna curentă, ci potrivit regulilor de corectare a erorilor contabile (prin rezultatul reportat, dacă sunt semnificative) și, dacă a afectat impozitul pe profit deja declarat, prin declarație rectificativă pentru perioadele respective.
- **Amortizarea fiscală curge de la luna următoare punerii în funcțiune**, indiferent când a fost efectiv calculată în sistem — deci recalcularea trebuie să refacă exact acest calendar, nu să pornească de la data descoperirii erorii.
- Durata normală de utilizare (DNF) rămasă nu se modifică pentru lunile omise — ele se recuperează ca amortizare neînregistrată, nu se „sar" definitiv, ceea ce ar reduce artificial baza de cheltuieli deductibile a firmei.

## Ce se greșește în practică

- Se „recuperează" amortizarea omisă printr-o singură sumă cumulată, înregistrată în luna curentă, fără a documenta pentru care luni anume a fost omisă și de ce — ceea ce face corecția greu de justificat la un control.
- Se ignoră lunile omise, presupunând că valoarea rămasă neamortizată se va recupera oricum până la finalul duratei normale de utilizare — de fapt, fără corectare explicită, activul riscă să rămână parțial neamortizat la finalul duratei sale.
- Se corectează perioade din ani fiscali deja închiși direct în luna curentă, fără declarație rectificativă pentru anul afectat, deși impozitul pe profit al acelui an a fost calculat cu o cheltuială de amortizare mai mică decât cea legal datorată.

## Ce face iConta.eu

Modulul de mijloace fixe din iConta.eu (`core/d406_active.py`, funcția `amortizare_luna`) calculează amortizarea lunară pe baza datei de punere în funcțiune, a duratei normale de funcționare și a metodei alese, iar `repo_mijloace_fixe.py` (`de_amortizat`) identifică activele cu amortizare de calculat într-o perioadă dată. La data acestui ghid, aplicația **nu are o funcție dedicată de recalculare automată retroactivă** a lunilor omise dintr-un exercițiu deja închis — corectarea unei amortizări omise pe câteva luni, mai ales dacă privește un an fiscal deja declarat, se face manual de contabil, cu documentarea perioadelor afectate.

[iConta.eu](/)
