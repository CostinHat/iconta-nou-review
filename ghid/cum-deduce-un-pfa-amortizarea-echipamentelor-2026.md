---
title: Cum deduce un PFA amortizarea echipamentelor în 2026?
description: De la 25.02.2026, pragul mijlocului fix amortizabil a crescut la 5.000 lei; peste acest prag, echipamentul se amortizează liniar, pe durata normală de funcționare din catalog, începând cu luna următoare punerii în funcțiune.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum deduce un PFA amortizarea echipamentelor în 2026?

Un echipament cumpărat de un PFA (laptop, imprimantă, utilaj, mobilier) nu se deduce integral, dintr-o dată, în luna cumpărării — dacă depășește pragul valoric al mijlocului fix, se recuperează treptat, prin amortizare, pe durata lui normală de funcționare. Anul 2026 aduce o schimbare importantă de prag, pe care merită s-o cunoști exact.

## Temeiul legal

::: ghid-temei
Codul fiscal, art. 28 alin. (2): "Mijlocul fix amortizabil este orice imobilizare corporală care îndeplinește cumulativ următoarele condiții: a) este deținut și utilizat în producția, livrarea de bunuri sau în prestarea de servicii, pentru a fi închiriat terților sau în scopuri administrative; b) la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei; această limită se actualizată anual, în funcție de indicele de inflație, prin hotărâre a Guvernului; c) are o durată normală de utilizare mai mare de un an." (nota de consolidare: litera b) a fost modificată de la 25-02-2026 prin OUG nr. 8/2026, anterior pragul fiind 2.500 lei, HG 276/2013)

Codul fiscal, art. 28 alin. (6): "amortizarea se stabilește prin aplicarea cotei de amortizare liniară la valoarea fiscală de la data intrării în patrimoniul contribuabilului a mijlocului fix amortizabil."

Codul fiscal, art. 28 alin. (12) lit. a): amortizarea începe "cu luna următoare celei în care mijlocul fix amortizabil se pune în funcțiune."

HG 2139/2004 (Catalogul mijloacelor fixe): "2.2.9. Calculatoare electronice și echipamente periferice. Mașini și aparate de casă, control și facturat. 2-4" (ani).
:::

## Pragul de 5.000 lei și durata din catalog

Din 25.02.2026, un echipament cu valoare de intrare de cel puțin 5.000 lei și durată normală de utilizare mai mare de un an este mijloc fix amortizabil. Sub acest prag, achiziția se trece direct pe cheltuială (obiect de inventar), fără amortizare. Durata pe care se face amortizarea nu e la alegere liberă — se ia din Catalogul privind clasificarea și duratele normale de funcționare a mijloacelor fixe (HG 2139/2004); pentru calculatoare și echipamente periferice, intervalul este 2-4 ani.

::: ghid-exemplu
Un PFA cumpără pe 10 martie 2026 un laptop de 6.500 lei, pus în funcțiune imediat, cu durată normală de utilizare aleasă din catalog de 3 ani (36 luni). Amortizarea începe din aprilie 2026 (luna următoare punerii în funcțiune). Cota lunară liniară este 6.500 / 36 ≈ 180,6 lei/lună, dedusă lunar până la epuizarea valorii.
:::

## Ce se greșește în practică

- Se deduce integral prețul echipamentului în luna cumpărării, tratându-l ca o cheltuială curentă, deși depășește pragul de mijloc fix.
- Se începe amortizarea din luna achiziției, nu din luna următoare punerii în funcțiune, cum cere art. 28 alin. (12) lit. a).
- Se alege arbitrar durata de amortizare, fără să se raporteze la intervalul din Catalogul HG 2139/2004.
- Se aplică din greșeală pragul vechi (2.500 lei) pentru achiziții făcute după 25.02.2026, deși pragul curent este 5.000 lei.
- Se confundă data facturii cu data punerii în funcțiune — punctul de plecare al amortizării e data de la care echipamentul e efectiv folosit, nu data cumpărării.

## Ce face iConta.eu

Amortizarea se calculează în `registru_inventar(conn, schema, an)` din `core/rip_api.py`: pentru fiecare mijloc fix se aplică metoda liniară pe lunile scurse din durata normală de funcționare (`amortizabil * luni / dnf_luni`), pe baza câmpurilor `data_pif`, `valoare` și `rezidual` din tabela `mijloace_fixe`. Important: funcția `registru_inventar()` **nu verifică ea însăși** dacă valoarea de intrare depășește pragul legal (5.000 lei de la 25.02.2026, conform `core/common.py`, `COTE["plafon_mijloc_fix"]`, și `core/obiecte_inventar.py`, `prag_mf()`) — citește tabela `mijloace_fixe` ca atare. Încadrarea unui bun ca mijloc fix sau ca obiect de inventar, prin raportare la prag, se face la introducerea achiziției, în modulul `core/mijloace_fixe_import_api.py`, nu în F077. Codul mai notează explicit că mijloacele fixe existente la 31.12.2025 cu valoare între 2.500 și 5.000 lei continuă să se amortizeze pe durata rămasă, fără reclasificare retroactivă.

[iConta.eu](/)
