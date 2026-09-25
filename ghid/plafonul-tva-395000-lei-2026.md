---
title: "Plafonul de TVA de 395.000 lei în 2026: cum se calculează"
description: "Ce intră în cifra de afaceri care se compară cu plafonul de scutire de TVA de 395.000 lei, potrivit art. 310 din Codul fiscal, valabil în 2026."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Plafonul de TVA de 395.000 lei în 2026: cum se calculează

Firmele mici pot rămâne neplătitoare de TVA cât timp cifra lor de afaceri nu depășește 395.000 lei pe an. Plafonul pare simplu, dar formula de calcul a cifrei de afaceri „de referință" nu coincide cu cifra de afaceri contabilă — include unele operațiuni scutite și exclude altele.

## Temeiul legal

::: ghid-temei
„Persoana impozabilă stabilită în România [...], a cărei cifră de afaceri anuală, declarată sau realizată, nu depășește plafonul de 395.000 lei, poate aplica scutirea de taxă, denumită în continuare regim special de scutire, pentru operațiunile prevăzute la art. 268 alin. (1), cu excepția livrărilor intracomunitare de mijloace de transport noi, scutite conform art. 294 alin. (2) lit. b)."
— Legea nr. 227/2015, art. 310 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Cifra de afaceri care servește drept referință pentru aplicarea alin. (1) este constituită din valoarea totală, exclusiv taxa [...], a livrărilor de bunuri și a prestărilor de servicii efectuate de persoana impozabilă în cursul unui an calendaristic, taxabile sau, după caz, care ar fi taxabile dacă nu ar fi desfășurate de o mică întreprindere, a operațiunilor scutite cu drept de deducere și, dacă nu sunt accesorii activității principale, a operațiunilor scutite fără drept de deducere prevăzute la art. 292 alin. (2) lit. a), b), e) și f), cu locul în România. Prin excepție, nu se cuprind în cifra de afaceri prevăzută la alin. (1) livrările de active fixe corporale [...] și cesiunea/transferul de active necorporale, efectuate de persoana impozabilă."
— Legea nr. 227/2015, art. 310 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Practic, în cifra de afaceri de referință intră:

- toate livrările de bunuri și prestările de servicii **taxabile** (sau care ar fi taxabile dacă firma n-ar fi la regim de scutire), exclusiv TVA;
- operațiunile **scutite cu drept de deducere** (ex. exporturi, livrări intracomunitare);
- operațiunile scutite **fără** drept de deducere de la art. 292 alin. (2) lit. a), b), e), f) (financiar-bancare, asigurări, pariuri/jocuri de noroc, terenuri și construcții) — dar **numai** dacă nu sunt accesorii activității principale.

Și nu intră: livrările de **active fixe corporale** și cesiunile de **active necorporale** — vânzarea unui utilaj sau a unui mijloc de transport din patrimoniu nu „umflă" plafonul.

## Ce se greșește în practică

- Se ia direct cifra de afaceri din balanța contabilă, fără să se scadă livrările de active fixe corporale sau cesiunile de active necorporale, care sunt expres excluse de art. 310 alin. (2).
- Se includ automat toate operațiunile scutite fără drept de deducere, deși legea le cere doar pe cele de la art. 292 alin. (2) lit. a), b), e), f), și doar dacă nu sunt accesorii activității principale.
- Se calculează plafonul pe an calendaristic fix, ignorând că pentru o firmă nou-înființată în cursul anului plafonul rămâne cel întreg de la alin. (1), fără proratare (art. 310 alin. (5)).

## Ce face iConta.eu

La data acestui ghid, iConta.eu urmărește vectorul de TVA al firmei (`tip_decont` — lunar/trimestrial) și generează **D300** (decontul de TVA) și **D394** pe baza facturilor introduse în aplicație, cu deducerea cotei per linie de factură. Aplicația nu calculează însă automat, ca funcție dedicată, cifra de afaceri de referință de la art. 310 alin. (2) pentru a semnala apropierea de plafonul de 395.000 lei — verificarea acestui plafon rămâne, la data acestui ghid, o operațiune manuală a utilizatorului sau a contabilului, pe baza facturilor emise evidențiate în aplicație.

[iConta.eu](/)
