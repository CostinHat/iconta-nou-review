---
title: "Veniturile din despăgubiri intră în plafonul micro?"
description: "Ce venituri se exclud, potrivit Codului fiscal, din baza impozabilă a microîntreprinderilor și dacă despăgubirile de la asigurări intră în calculul plafonului de încadrare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Veniturile din despăgubiri intră în plafonul micro?

Nu orice sumă încasată de o microîntreprindere devine automat parte din baza de calcul a impozitului pe veniturile microîntreprinderilor. Codul fiscal exclude explicit anumite categorii de venituri, iar despăgubirile de la asigurări sunt printre ele — dar exact în ce condiții.

## Temeiul legal

::: ghid-temei
„Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie veniturile din orice sursă, din care se scad: [...] g) veniturile realizate din despăgubiri, de la societățile de asigurare/reasigurare, pentru pagubele produse bunurilor de natura stocurilor sau a activelor corporale proprii."
— Legea 227/2015, art. 53 alin. (1) lit. g) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din text rezultă o distincție care nu ține de plafonul de încadrare la micro (cel de 100.000 euro de la art. 47), ci de **baza impozabilă lunară/trimestrială** pe care se aplică cota de impozit micro:

- Sunt **excluse din baza de calcul a impozitului** (deci nu se impozitează cu cota micro) doar despăgubirile **de la societăți de asigurare/reasigurare**, primite pentru pagube produse **stocurilor sau activelor corporale proprii**.
- Textul nu exclude orice fel de despăgubire — o despăgubire contractuală primită de la un partener comercial (de exemplu penalizare/despăgubire pentru neexecutarea unui contract), care nu vine de la un asigurător, rămâne, potrivit acestei liste, venit impozabil cu cota micro.
- Excluderea de la art. 53 privește baza de impozitare, nu plafonul de 100.000 euro de la art. 47 pentru încadrarea ca microîntreprindere — cele două verificări sunt distincte, iar acest ghid nu poate confirma din texul citat dacă despăgubirile excluse la art. 53 se exclud și din calculul plafonului de încadrare, aspect nereglementat explicit în sursele disponibile.

## Ce se greșește în practică

- Se exclude din baza impozabilă orice sumă etichetată „despăgubire", indiferent de la cine vine — condiția legală e strictă: societate de asigurare/reasigurare, pentru pagube la stocuri sau active corporale proprii.
- Se confundă excluderea din baza de impozitare (art. 53) cu excluderea din plafonul de încadrare ca microîntreprindere (art. 47) — sunt praguri și mecanisme diferite, iar textul citat vizează explicit doar baza de impozitare.
- Se impozitează cu cota micro despăgubirile de asigurare pentru bunuri proprii, din reflex de a impozita orice venit înregistrat în clasa 7, ignorând excluderea explicită de la art. 53 alin. (1) lit. g).

## Ce face iConta.eu

Motorul de calcul al bazei micro din iConta.eu însumează veniturile din conturile de clasa 7 (70x, 75x, 76x) și scade reducerile comerciale acordate ulterior facturării (contul 709), conform structurii generale a art. 53 din Codul fiscal — mecanism confirmat de testele interne care validează baza micro pe „venituri din orice sursă minus 709". La data acestui ghid nu există, în aplicație, o verificare punctuală care să identifice automat o încasare drept „despăgubire de asigurare pentru pagube la stocuri/active proprii" și s-o excludă separat din baza impozabilă — încadrarea corectă a unei astfel de sume, în contul potrivit și cu excluderea aferentă, rămâne responsabilitatea contabilului la înregistrare.

[iConta.eu](/)
