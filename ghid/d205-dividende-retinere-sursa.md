---
title: D205 pentru dividende cu reținere la sursă
description: Reținerea la sursă nu e un caz special — e mecanismul standard prin care se impozitează orice dividend. Cine reține, când, cât și până când se virează impozitul.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# D205 pentru dividende cu reținere la sursă

Toate dividendele plătite unor persoane fizice sunt impozitate prin reținere la sursă — nu e o opțiune sau un caz special, e regula generală de impozitare a dividendelor în România. Societatea care plătește dividendul calculează, reține și virează impozitul; beneficiarul primește deja suma netă. D205 este declarația prin care societatea raportează, la nivel de fiecare beneficiar, baza de impozitare și impozitul reținut.

## Temeiul legal

::: ghid-temei
"(7) Veniturile sub formă de dividende, inclusiv câștigul obținut ca urmare a deținerii de titluri de participare definite de legislația în materie la organisme de plasament colectiv, se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor/sumelor reprezentând câștigul obținut ca urmare a deținerii de titluri de participare de către acționari/asociați/investitori. Termenul de virare a impozitului este până la data de 25 inclusiv a lunii următoare celei în care se face plata."
— Codul fiscal, Legea 227/2015, art. 97 alin. (7)
:::

Trei lucruri rezultă direct din text: (1) obligația de calcul și reținere e a societății plătitoare, nu a beneficiarului; (2) momentul reținerii e plata efectivă a dividendului, nu data la care a fost aprobată distribuirea; (3) impozitul reținut e final — beneficiarul nu mai datorează impozit pe venit suplimentar pentru acea sumă.

## Ce se greșește în practică

- Se confundă termenul de **virare a impozitului reținut** (25 a lunii următoare plății) cu termenul de **depunere a declarației D205** (ultima zi a lunii februarie a anului următor celui raportat) — sunt două termene diferite, cu regim diferit.
- Se crede că beneficiarul trebuie să declare separat venitul din dividende la impozitul pe venit — nu e cazul, impozitul reținut la sursă e final pentru acest tip de venit.
- Se reține impozitul la data aprobării distribuirii (hotărârea AGA), nu la data plății efective — reținerea și virarea sunt legate de plată, nu de distribuire.

## Ce face iConta.eu

iConta.eu calculează baza de impozitare și impozitul reținut pe **dividendul plătit** (nu pe cel distribuit), citind mișcările contului 457 din note contabile validate — debitul 457 (plata efectivă) e cel care generează `baza1`/`imp1` în D205. Cota aplicată este cea în vigoare la data la care dividendul a fost **distribuit** (nu neapărat cea din anul plății), potrivită automat pe tranșe atunci când plata e eșalonată sau se face în alt an decât distribuirea. Fiecare beneficiar este validat pe CNP (cifră de control) înainte de a intra în declarație.

[iConta.eu](/)
