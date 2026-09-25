---
title: "Cum se tratează TVA la dropshipping în UE?"
description: "Regimul special OSS pentru vânzările intracomunitare de bunuri la distanță, aplicabil și modelelor de dropshipping cu stoc situat într-un stat membru UE — cu limitele reale ale acestui temei pentru lanțuri de livrare mai complexe."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se tratează TVA la dropshipping în UE?

Dropshipping-ul nu e un regim de TVA distinct în Codul fiscal — tratamentul depinde de unde se află efectiv bunul la momentul vânzării și cine face transportul. Pentru varianta cea mai frecventă (stoc într-un stat membru UE, vândut către clienți persoane fizice din alte state membre), regimul relevant este cel al vânzărilor intracomunitare de bunuri la distanță.

## Temeiul legal

::: ghid-temei
„Prezentul regim special poate fi utilizat de către orice persoană impozabilă care are sediul activității economice în România sau, în cazul în care nu are sediul activității economice în Uniunea Europeană, dispune de un sediu fix în România. [...] Regimul special poate fi utilizat în următoarele cazuri: a) de către orice persoană impozabilă care efectuează vânzări intracomunitare de bunuri la distanță. Regimul special poate fi utilizat și de către orice persoană impozabilă care nu are sediul activității economice în Uniunea Europeană și nici nu dispune de un sediu fix în România, dar efectuează vânzări intracomunitare la distanță care au locul de începere a expedierii sau transportului bunurilor în România."
— Legea nr. 227/2015 (Codul fiscal), art. 315 alin. (2) lit. a) — regimul special pentru vânzările intracomunitare de bunuri la distanță (OSS UE); nu se confundă cu art. 315^1, care reglementează regimul special pentru agricultori (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă, cu limitele reale ale acestui temei:

- Dacă firma românească deține (sau folosește printr-un terț) **stoc fizic într-un stat membru UE** și vinde de acolo către clienți persoane fizice din alte state membre, operațiunea e o **vânzare intracomunitară de bunuri la distanță**, care poate fi declarată prin regimul special **OSS**, evitând înregistrarea separată de TVA în fiecare stat de destinație.
- Sub pragul unic de 10.000 euro (cumulat la nivelul UE, vezi art. 278^1), se poate aplica TVA din statul membru de origine; peste prag, TVA se datorează în statul membru al clientului, declarată prin OSS.
- **Limita reală a acestui ghid**: modelele de dropshipping în care marfa nu trece niciodată prin stocul firmei românești, ci e expediată direct de un furnizor din afara UE către clientul final, implică reguli diferite (import de bunuri de mică valoare, regimul IOSS pentru bunuri sub 150 euro, sau lanțuri de livrare cu mai mulți intermediari) — pentru aceste variante, nu am identificat în sursele verificate un temei suficient de precis încât să îl cităm fără riscul unei simplificări excesive, așa că recomandăm verificarea punctuală a fiecărui flux de livrare cu un consultant fiscal.

## Ce se greșește în practică

- Se tratează orice vânzare online cu livrare din altă țară drept „vânzare la distanță" cu regim OSS, fără să se verifice dacă marfa a trecut vreodată prin stocul firmei sau a fost expediată direct de furnizor către client.
- Se ignoră faptul că, pentru bunurile expediate direct din afara UE către clientul final, regimul relevant e altul (import, eventual IOSS), nu vânzarea intracomunitară la distanță de la art. 315.
- Se presupune că înregistrarea în OSS elimină automat orice altă obligație de TVA, deși lanțuri de livrare mai complexe (cu mai mulți intermediari) pot implica reguli suplimentare de tratare a operațiunilor triunghiulare.

## Ce face iConta.eu

iConta.eu emite facturile aferente vânzărilor online și ține evidența operațiunilor introduse de utilizator, dar **nu determină automat** dacă o vânzare concretă de tip dropshipping se încadrează la vânzare intracomunitară la distanță, la import de bunuri de mică valoare sau la o operațiune triunghiulară — încadrarea corectă, în funcție de fluxul real de marfă, rămâne o decizie a utilizatorului/contabilului la momentul facturării. Pentru firmele deja înregistrate în regimul OSS, aplicația are un modul de generare a declarației D398 (`core/d398.py`), dar aceasta se completează manual, pe valori introduse de contabil per stat membru de consum — aplicația nu deduce automat aceste valori din operațiunile de dropshipping înregistrate.

[iConta.eu](/)
