---
title: "TVA pentru vânzările prin marketplace-uri străine"
description: "Regula pragului de 10.000 euro pentru vânzările la distanță către consumatori din alte state membre și rolul regimului special OSS atunci când firma vinde prin marketplace-uri străine."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# TVA pentru vânzările prin marketplace-uri străine

Vânzarea de bunuri către persoane fizice din alte state membre, prin marketplace-uri precum Amazon, eBay sau eMAG internațional, nu se taxează automat cu TVA românesc. Locul livrării — și, deci, statul căruia i se datorează TVA — depinde de un prag valoric anual, comun tuturor vânzărilor de acest tip din UE.

## Temeiul legal

::: ghid-temei
„(1) Prevederile art. 275 alin. (2) și art. 278 alin. (5) lit. h) nu se aplică dacă sunt îndeplinite cumulativ următoarele condiții: a) furnizorul sau prestatorul este stabilit sau, dacă nu este stabilit, își are domiciliul stabil sau reședința obișnuită într-un singur stat membru; [...] b) sunt prestate servicii către persoane neimpozabile care sunt stabilite, își au domiciliul stabil sau reședința obișnuită în orice stat membru, altul decât statul membru prevăzut la lit. a), sau sunt expediate ori transportate bunuri către un stat membru, altul decât statul membru prevăzut la lit. a); și c) valoarea totală, fără TVA, a operațiunilor prevăzute la lit. b) nu depășește, în anul calendaristic curent, 10.000 euro sau echivalentul acestei sume în moneda națională și nici nu a depășit această sumă în cursul anului calendaristic precedent.
(2) Atunci când, în cursul unui an calendaristic, pragul prevăzut la alin. (1) lit. c) este depășit, prevederile art. 275 alin. (2) și art. 278 alin. (5) lit. h) se aplică de la momentul depășirii pragului."
— Legea nr. 227/2015 (Codul fiscal), art. 278^1 alin. (1), (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Concret, pentru o firmă românească ce vinde consumatori (persoane neimpozabile) din alte state UE prin marketplace:

- **Sub 10.000 euro cumulat pe an** (toate vânzările la distanță + serviciile electronice către alte state membre, luate împreună, nu pe fiecare țară separat), locul livrării rămâne România și se aplică TVA românesc, ca la orice vânzare internă.
- **Peste pragul de 10.000 euro**, de la momentul depășirii, locul livrării devine statul membru de destinație — firma datorează TVA la cota din țara cumpărătorului, pentru fiecare livrare ulterioară pragului.
- Pentru a evita înregistrarea în scopuri de TVA în fiecare stat membru în care are clienți, firma poate opta pentru **regimul special UE (OSS — One Stop Shop)**, prin care declară și plătește centralizat, din România, TVA-ul datorat tuturor celorlalte state membre.
- Regula se aplică indiferent de canalul de vânzare (site propriu sau marketplace); ceea ce contează este statul de reședință al cumpărătorului final, nu platforma prin care s-a făcut vânzarea.

## Ce se greșește în practică

- Se aplică TVA românesc pe toate vânzările din marketplace, fără să se urmărească pragul cumulat de 10.000 euro pe an calendaristic.
- Se calculează pragul separat, pe fiecare țară de destinație, în loc de cumulat la nivelul tuturor vânzărilor la distanță din UE, așa cum cere art. 278^1 alin. (1) lit. c).
- Se confundă TVA-ul reținut/perceput de marketplace (dacă platforma aplică regulile de „furnizor considerat" pentru vânzători din afara UE) cu obligația proprie de TVA a firmei românești, care rămâne, de regulă, subiect al regimului OSS, nu al platformei.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu calculează automat pragul de 10.000 euro** și nu depune declarația OSS. Aplicația are un modul de taxare inversă și validare VIES pentru operațiuni intracomunitare (`core/intracomunitar.py`), folosit în principal la achiziții, precum și cote de TVA gestionate pe firmă (`core/cote_tva.py`), dar nu urmărește cumulat vânzările la distanță ale unei firme către consumatori din alte state membre și nu semnalează depășirea pragului. Singurul conector de vânzări automate este cel pentru WooCommerce (`core/woocommerce.py`); urmărirea plafonului OSS și aplicarea cotei corecte de TVA a statului de destinație rămân, în prezent, în sarcina contabilului.

[iConta.eu](/)
