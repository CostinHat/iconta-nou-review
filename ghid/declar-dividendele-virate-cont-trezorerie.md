---
title: "Cum declar dividendele virate pe un cont de trezorerie"
description: "Regulile de reținere, declarare și plată a impozitului pe dividende atunci când sumele sunt virate prin bancă (conturi de trezorerie), valabile pentru 2026."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum declar dividendele virate pe un cont de trezorerie

Indiferent dacă dividendele ajung la asociat printr-un virament obișnuit sau printr-un cont de trezorerie (clasa 5 de conturi — 512 „Conturi curente la bănci"), obligația fiscală e aceeași: societatea care plătește dividendul reține impozitul la sursă, îl declară și îl virează la buget. Momentul care contează nu este data plății efective din contul de trezorerie, ci data la care dividendul a fost distribuit, respectiv data la care este efectiv plătit asociatului.

## Temeiul legal

::: ghid-temei
„Veniturile sub formă de dividende, inclusiv câștigul obținut ca urmare a deținerii de titluri de participare definite de legislația în materie la organisme de plasament colectiv, se impozitează cu o cotă de **16%** din suma acestora, impozitul fiind final. Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor [...] Termenul de virare a impozitului este până la data de **25 inclusiv a lunii următoare** celei în care se face plata."
— Legea nr. 227/2015 (Codul fiscal), art. 97 alin. (7), astfel cum a fost modificat prin Legea nr. 141/2025 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Câteva repere pentru declarare, indiferent de contul prin care circulă banii:

- Impozitul se calculează și se reține **la data plății** dividendului către asociat/acționar, nu la data la care societatea decide distribuirea.
- Cota de **16%** se aplică dividendelor distribuite începând cu 1 ianuarie 2026; dividendele interimare distribuite în 2025 au rămas la cota de **10%**, fără recalculare ulterioară, chiar dacă plata sau regularizarea are loc în 2026 — deci data distribuirii, nu data plății, decide cota aplicabilă.
- Dacă dividendele au fost aprobate dar nu au fost plătite până la sfârșitul anului, impozitul se declară și se plătește până la **25 ianuarie** a anului următor.
- Declararea impozitului reținut se face prin declarația specifică veniturilor din investiții/dividende (D205 pentru persoane fizice), depusă de plătitorul de venit.

## Ce se greșește în practică

- Se calculează impozitul la cota valabilă la data plății efective, ignorând faptul că pentru dividendele distribuite în 2025 (dar plătite ulterior) legea a păstrat cota de 10% aplicabilă la data distribuirii.
- Se omite declararea impozitului pentru dividendele aprobate și nedistribuite până la 31 decembrie — termenul de 25 ianuarie al anului următor se aplică indiferent dacă suma a rămas fizic în contul societății.
- Se tratează contul de trezorerie ca „altă categorie" de plată, deși din punct de vedere fiscal contează doar fluxul (data creditării contului asociatului), nu tipul de cont bancar prin care circulă suma.

## Ce face iConta.eu

Da — iConta.eu are un modul dedicat pentru acest calcul (`dividende_curs.py`), care atribuie plățile de dividende pe distribuiri, în ordine cronologică (FIFO), astfel încât impozitul să fie aplicat cu cota valabilă la **data distribuirii** fiecărei tranșe, nu cu cota de la data plății. Motorul e construit explicit pe baza art. 97 alin. (7) din Codul fiscal și pe tranziția de cotă adusă de Legea nr. 141/2025 (10% pentru distribuirile din 2025, 16% pentru cele din 2026), fiind folosit atât la generarea, cât și la reconcilierea declarației D205.

[iConta.eu](/)
