---
title: "Se declară achizițiile de la persoane fizice în D394?"
description: "Când și cum apar în declarația 394 achizițiile de bunuri de la persoane fizice, defalcate pe cod de produs în secțiunea op11."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se declară achizițiile de la persoane fizice în D394?

Da, dar spre deosebire de facturile emise către persoane fizice — care se cumulează într-un rezumat — achizițiile de bunuri de la persoane fizice se raportează defalcat, pe fiecare cod de produs în parte, într-o secțiune specială a declarației.

## Temeiul legal

::: ghid-temei
„<op11> [...] Aparitie numai pentru tip in (L,A,V,C,AI) pt tip_partener=1 și tip=N pt (tip_partener=2 și cota=0). Pt ((tip în (V,C) și tip_partener=1) sau (tip=N și (lung(cuiP)=13 sau cuiP=null))) sectiunea este obligatorie."
„codPR — Cod produs [...] Verificare cu nomenclator produse — Verificare unicitate apariție codPR — ERR - Cod produs necompletat."
„bazaPR — Bază impozabilă [...] ERR - bază impozabilă necompletată."
— Structura oficială D394, poziția 233–236 (sursă: anaf_surse/d394_struct_anaf.txt)
:::

Pentru o achiziție de bunuri de la o persoană fizică fără CUI valid, D394 cere:

- încadrarea operațiunii la tipul **N** (fără drept de deducere, partener neînregistrat, cotă 0);
- deschiderea secțiunii **op11**, obligatorie exact în acest caz (tip_partener=2 fără CUI valid și cotă 0);
- completarea codului de produs (**codPR**), verificat față de nomenclatorul de produse al ANAF, cu bază impozabilă proprie pentru fiecare cod.

Important: pentru ca taxarea inversă (art. 331 CF) să se aplice unei achiziții de bunuri de la lista de la art. 331 alin. (2) — cereale, deșeuri feroase/neferoase, masă lemnoasă etc. — legea cere ca **ambele părți** să fie înregistrate în scopuri de TVA. O achiziție de la o persoană fizică neînregistrată nu intră sub acest regim; raportarea prin `op11`/`codPR` e informativă, nu generează TVA deductibilă.

## Ce se greșește în practică

- Se omite complet declararea achiziției de la persoana fizică, considerând că, fără CUI de partener, nu există nimic de raportat — secțiunea `op11` e totuși obligatorie în acest caz.
- Se aplică taxare inversă unei achiziții de cereale sau deșeuri de la o persoană fizică neînregistrată în scopuri de TVA, deși art. 331 alin. (1) cere expres ca și furnizorul să fie înregistrat.
- Se lasă necompletat codul de produs (`codPR`), deși validatorul oficial îl cere explicit și verifică unicitatea apariției lui.

## Ce face iConta.eu

La data acestui ghid, iConta.eu clasifică automat partenerii fără CUI valid de pe facturile de achiziție și, pentru cei care necesită defalcare pe cod de produs conform structurii oficiale, verifică prezența categoriei de bun (`codPR`, derivată din categoria art. 331 înscrisă pe factură). Dacă aceasta lipsește, aplicația **nu respinge generarea întregii declarații**: exclude explicit acea operațiune din D394 și afișează un avertisment cu furnizorul și suma exclusă, restul declarației rămânând valid și generabil (`core/d394.py`) — nu o omite tacit. Adăugarea categoriei corecte pe factură, pentru ca operațiunea să fie inclusă, rămâne responsabilitatea utilizatorului.

[iConta.eu](/)
