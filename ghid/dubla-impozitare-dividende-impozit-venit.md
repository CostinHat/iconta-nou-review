---
title: "Dubla impozitare dividende: impozit pe venit și CASS"
description: Nu e, strict vorbind, o dublă impozitare — sunt două obligații fiscale diferite, cu debitori diferiți, pe același venit din dividende. Ce acoperă D205 și ce nu acoperă.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Dubla impozitare dividende: impozit pe venit și CASS

Mulți beneficiari de dividende au impresia unei "duble impozitări" atunci când, pe lângă impozitul de 16% reținut de societate, se pomenesc și cu o obligație de contribuție la sănătate (CASS) pe același venit. Din punct de vedere legal nu e o dublă impozitare a aceleiași obligații, ci două obligații distincte, cu reguli și debitori diferiți: impozitul pe venitul din dividende (reținut de societatea plătitoare) și contribuția de asigurări sociale de sănătate (datorată de beneficiar, ca persoană fizică, pe cumulul veniturilor sale).

## Temeiul legal

::: ghid-temei
"(7) Veniturile sub formă de dividende, inclusiv câștigul obținut ca urmare a deținerii de titluri de participare definite de legislația în materie la organisme de plasament colectiv, se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor/sumelor reprezentând câștigul obținut ca urmare a deținerii de titluri de participare de către acționari/asociați/investitori."
— Codul fiscal, Legea 227/2015, art. 97 alin. (7)
:::

Acest text acoperă exclusiv **impozitul pe venit** din dividende — reținut de societate, la plată, cu titlu final. Cercetarea care stă la baza acestui ghid nu a inclus o verificare punctuală a textelor de lege privind CASS (praguri de venit, plafoane exprimate în salarii minime, mod de calcul) pentru funcționalitatea F029/D205 — acestea nu sunt tratate de motorul D205 din iConta.eu, așa că nu redăm aici cote, plafoane sau proceduri de CASS pe care nu le putem susține cu o sursă verificată în acest dosar. Ce putem confirma cu certitudine e distincția structurală: impozitul pe dividende e o obligație a **societății plătitoare** (reținere la sursă, declarată prin D205), în timp ce eventuala contribuție de asigurări sociale de sănătate pe veniturile din dividende e o obligație a **beneficiarului persoană fizică**, declarată separat, prin propria lui declarație.

## Ce se greșește în practică

- Se consideră că impozitul de 16% reținut prin D205 "acoperă tot" ce datorează beneficiarul pentru acel venit — de fapt privește doar impozitul pe venit; o eventuală obligație de CASS, dacă există, se stabilește și se declară separat de beneficiar.
- Se așteaptă ca societatea plătitoare (și, implicit, D205) să calculeze sau să rețină și CASS pe dividend — nu e rolul D205; D205 raportează exclusiv impozitul pe venitul din dividende reținut de societate.
- Se cere iConta.eu să avertizeze automat un beneficiar că depășește un prag de CASS pe dividende — funcționalitatea F029/D205 nu urmărește cumulul veniturilor beneficiarului pe alte categorii și nu emite un asemenea avertisment; e o limitare cunoscută, nu o funcție existentă.

## Ce face iConta.eu

Funcționalitatea F029/D205 din iConta.eu gestionează exclusiv impozitul pe dividende reținut la sursă de societatea plătitoare — calculat pe dividendul plătit, la cota valabilă la data distribuirii, și declarat prin D205. Aplicația nu calculează, nu urmărește și nu avertizează cu privire la o eventuală obligație de CASS a beneficiarului persoană fizică pe veniturile din dividende — aceasta rămâne, integral, în sarcina beneficiarului, prin propria lui declarație. Dacă sunteți beneficiar de dividende și vreți să știți dacă intrați sub incidența CASS, verificați separat, cu un consultant fiscal, regimul aplicabil cumulului dumneavoastră de venituri.

[iConta.eu](/)
