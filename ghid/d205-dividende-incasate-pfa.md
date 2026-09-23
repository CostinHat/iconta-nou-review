---
title: D205 pentru dividende încasate de un PFA
description: Dividendele încasate de o persoană care e și titular de PFA se impozitează exact ca la orice altă persoană fizică asociată — venitul din dividende nu se amestecă cu venitul din activitatea independentă.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# D205 pentru dividende încasate de un PFA

O persoană poate fi, simultan, titular de PFA și asociat/acționar într-o societate. Cele două calități sunt complet separate fiscal: veniturile din activitatea independentă (PFA) urmează regimul lor propriu, iar dividendele încasate ca asociat urmează regimul dividendelor — impozit final de 16% (sau cota istorică aplicabilă), reținut la sursă de societate. Faptul că beneficiarul are și un PFA nu schimbă cu nimic tratamentul dividendului.

## Temeiul legal

::: ghid-temei
"(7) Veniturile sub formă de dividende [...] se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor/sumelor reprezentând câștigul obținut ca urmare a deținerii de titluri de participare de către acționari/asociați/investitori."
— Codul fiscal, Legea 227/2015, art. 97 alin. (7)
:::

Legea leagă impozitarea dividendului de calitatea de acționar/asociat, nu de alte activități fiscale ale beneficiarului. Un PFA care e și asociat rămâne, pentru veniturile din dividende, un beneficiar obișnuit de dividend — nimic din text nu introduce un regim diferit pentru cine are și venituri din activitate independentă.

## Ce se greșește în practică

- Se încearcă raportarea dividendului încasat ca venit al PFA-ului (de exemplu ca venit din activitatea independentă) — dividendul nu e, fiscal, venit din activitate independentă, ci venit din deținerea de titluri de participare; regimul lui (16%, reținut la sursă, final) e complet distinct.
- Se presupune că impozitul de 16% reținut prin D205 acoperă și eventuale obligații de CASS pe care beneficiarul, ca persoană fizică, le poate avea pe cumulul veniturilor sale (inclusiv dividende) — impozitul pe dividend și contribuția de asigurări sociale de sănătate sunt obligații diferite; a doua e a beneficiarului, declarată separat de acesta, nu de societatea plătitoare.
- Se așteaptă ca D205 sau iConta.eu să semnaleze automat o eventuală obligație de CASS a beneficiarului — funcționalitatea F029 nu emite un asemenea avertisment; rămâne responsabilitatea beneficiarului să verifice, prin propria declarație, dacă intră sub incidența CASS.

## Ce face iConta.eu

Generatorul D205 din iConta.eu identifică fiecare beneficiar exclusiv după CNP (validat pe cifră de control) și cota lui de participare în societate — nu ține cont, și nu are de unde să țină cont, de faptul că beneficiarul respectiv are și calitatea de titular PFA. Dividendul acelui asociat e calculat și declarat exact ca la orice alt beneficiar persoană fizică: baza pe dividendul plătit, cota valabilă la data distribuirii, impozit final.

[iConta.eu](/)
