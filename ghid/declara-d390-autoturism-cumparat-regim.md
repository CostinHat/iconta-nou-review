---
title: "Se declară în D390 un autoturism cumpărat în regim de marjă?"
description: "De ce achiziția unui autoturism second-hand facturat în regim special de marjă de către un dealer din UE nu apare în declarația recapitulativă D390."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se declară în D390 un autoturism cumpărat în regim de marjă?

Nu. Dacă vânzătorul dintr-un alt stat membru UE a facturat autoturismul second-hand în regim special de marjă (echivalentul art. 312 din Codul fiscal aplicat de el, în țara lui), achiziția nu se declară în D390 la rubrica „Achiziții intracomunitare de bunuri" (codul A). Motivul nu e o excepție tehnică de completare a formularului, ci faptul că operațiunea nici nu e, din capul locului, o achiziție intracomunitară impozabilă în România.

## Temeiul legal

::: ghid-temei
„c) Achiziţii intracomunitare de bunuri – se înscrie suma totală a achiziţiilor intracomunitare de bunuri, pe fiecare furnizor, pentru care persoana impozabilă, care depune declaraţia, este obligată la plata taxei conform art. 308 din Codul fiscal, şi pentru care exigibilitatea taxei intervine în luna calendaristică respectivă, inclusiv sumele din facturile primite pentru plăţi de avansuri pentru achiziţii intracomunitare de bunuri."
— OPANAF 394/2017, Anexa 2 (Instrucțiuni D390 VIES), Secțiunea a 2-a, pct. 1 lit. c) (sursă: anaf_surse/opanaf_394_2017_d390_anexa2_instructiuni.txt)
:::

D390 declară, la rubrica „A", strict achizițiile intracomunitare **pentru care cumpărătorul din România e obligat la plata taxei** (autolichidare, conform art. 308 din Codul fiscal). Iar Codul fiscal exclude explicit din categoria operațiunilor impozabile achiziția de bunuri second-hand facturate în regim de marjă de un dealer din UE:

- Codul fiscal, art. 268 alin. (8) lit. c): „Nu sunt considerate operațiuni impozabile în România [...] achizițiile intracomunitare de bunuri second-hand [...] în sensul prevederilor art. 312, atunci când vânzătorul este o persoană impozabilă revânzătoare, care acționează în această calitate, iar bunurile au fost taxate în statul membru de unde sunt furnizate, conform regimului special [...]" (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt).
- Cum nu e o achiziție impozabilă, cumpărătorul **nu e obligat la plata taxei conform art. 308** — deci nu se încadrează în definiția rubricii A din instrucțiunile D390 de mai sus.

Concluzia curge direct din lanțul celor două texte: nefiind o operațiune „pentru care persoana impozabilă este obligată la plata taxei conform art. 308", achiziția nu are ce căuta în declarația recapitulativă.

## Ce se greșește în practică

- Se declară automat, în D390, orice factură primită de la un furnizor din UE identificat cu cod de TVA, fără să se verifice dacă acea achiziție e într-adevăr impozabilă în România sau exclusă conform art. 268 alin. (8).
- Se confundă „nu apare în D390" cu „factura nu se înregistrează contabil deloc" — achiziția tot trebuie înregistrată în contabilitate (intrarea mașinii la cost), doar că fără linie de TVA și fără raportare recapitulativă.
- Se declară eronat operațiunea cu codul „A", generând o diferență între ce apare în D390 la nivelul furnizorului din UE (care, la rândul lui, poate să nu fi raportat nimic reciproc, tocmai fiindcă a vândut în regim de marjă) și ce raportează cumpărătorul.

## Ce face iConta.eu

Această întrebare privește exclusiv declarația D390 și tratamentul unei achiziții intracomunitare — nu are legătură cu funcționalitatea „Jurnal regim marjă" din iConta.eu, care e un raport de citire pentru **vânzările** proprii înregistrate în regim special de marjă (second-hand sau turism), nu pentru achiziții. Verificat: modulul de completare D390 din aplicație (`core/d390.py`) nu conține nicio linie legată de regimul de marjă sau de art. 312 — deci aplicația nu are, la data acestui ghid, o excludere automată a acestui tip de achiziție din baza de calcul a D390. Contabilul trebuie să recunoască manual acest caz și să nu introducă factura respectivă în circuitul care alimentează D390.

[iConta.eu](/)
