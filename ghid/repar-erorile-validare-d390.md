---
title: "Cum repar erorile de validare din D390?"
description: "Ghid practic pentru identificarea și corectarea celor mai frecvente erori de validare la depunerea declarației D390 (VIES) în iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum repar erorile de validare din D390?

Declarația recapitulativă D390 (VIES) e supusă unor reguli stricte, atât legale, cât și tehnice. De cele mai multe ori, "eroarea de validare" nu e o problemă de format, ci un semnal despre o condiție de fond neîndeplinită — cod de TVA invalid, clasificare greșită a operațiunii sau lipsa unui document justificativ. Mai jos sunt situațiile cele mai des întâlnite și felul în care le tratează aplicația.

## Temeiul legal

::: ghid-temei
„Orice persoană impozabilă înregistrată în scopuri de TVA conform art. 316 sau 317 trebuie să întocmească și să depună la organele fiscale competente o declarație recapitulativă…” — Codul fiscal (Legea 227/2015), art. 325 alin. (1) (`cod_fiscal_227_2015_consolidat.txt:22103`)

„Sunt, de asemenea, scutite de taxă următoarele: a) livrările intracomunitare de bunuri către o persoană impozabilă... care îi comunică furnizorului un cod valabil de înregistrare în scopuri de TVA, atribuit de autoritățile fiscale din alt stat membru…” — Codul fiscal, art. 294 alin. (2) lit. a) (`cod_fiscal_227_2015_consolidat.txt:18514-18525`)

„Scutirea prevăzută la alin. (2) lit. a) nu se aplică în cazul în care furnizorul nu a respectat obligația prevăzută la art. 325 alin. (1) de a depune o declarație recapitulativă sau declarația recapitulativă depusă de acesta nu conține informațiile corecte…” — Codul fiscal, art. 294 alin. (2^1) (`cod_fiscal_227_2015_consolidat.txt:18549-18552`)
:::

Aceste prevederi arată de ce validarea D390 nu se oprește la formatul XML: o declarație depusă greșit sau incomplet poate anula chiar scutirea de TVA a livrării intracomunitare pe care o raportează.

## Ce se greșește în practică

- **Confuzia dintre codurile P și S.** P înseamnă servicii vândute de firma română unui client din UE (loc de prestare la client, art. 278 alin. (2) CF); S înseamnă servicii cumpărate de la un prestator din UE (taxare inversă la beneficiar, art. 307 alin. (2) CF). Aceeași logică se aplică bunurilor: L = vândute, A = cumpărate.
- **Se presupune că un cod de TVA valid în VIES e suficient** pentru scutirea livrării intracomunitare de bunuri (cod L). Nu este — pe lângă codul valid, e nevoie și de justificarea documentară a scutirii (de regulă, dovada transportului bunurilor în alt stat membru).
- **Se ignoră cazul special al furnizorului fără cod de TVA valid** la o achiziție intracomunitară de bunuri: chiar și atunci, dacă bunurile sunt transportate efectiv dintr-un stat membru UE, achiziția tot trebuie declarată (tip A) — coloana "Cod operator" rămâne necompletată, dar țara este obligatorie.
- **Se scrie "CR" pentru Croația**, în loc de codul corect "HR".
- **Se presupune că D390 poate fi depusă trimestrial** dacă firma are perioadă fiscală trimestrială la D300 (decontul de TVA). D390 este întotdeauna lunară, indiferent de periodicitatea TVA a firmei.

## Ce face iConta.eu

- Pentru majoritatea statelor UE, aplicația **nu verifică local** cifra de control a codului de TVA — se bazează pe interogarea VIES live. Verificarea offline a cifrei de control există doar pentru Germania (DE), Croația (HR) și Franța (FR); pentru celelalte state, codul rămâne "neverificat" local până la interogarea VIES. Dacă serviciul VIES e indisponibil, aplicația nu poate confirma validitatea codului.
- Un cod de TVA invalid în VIES generează în aplicație un **avertisment, nu un blocaj**: operațiunea se emite oricum, ca să nu dispară tăcut din declarație. Decizia finală privind aplicarea TVA rămâne, în acest caz, în sarcina contabilului.
- Pentru livrarea intracomunitară de bunuri, aplicația aplică o **dublă condiție**: cod TVA valid în VIES ȘI dovadă de transport. Pe ecranul de emitere, câmpul "dovadă transport" este marcat opțional vizual, dar este obligatoriu funcțional pentru bunuri — fără el, scutirea este respinsă de server. Pentru servicii, este suficient codul VIES valid.
- La achiziția intracomunitară, aplicația cere obligatoriu codul de TVA al furnizorului — fără el, achiziția nu ajunge deloc în D390. Tipul operațiunii (bunuri/servicii) este validat strict față de nomenclator; o valoare greșită nu mai este atribuită implicit categoriei "bunuri".
- Codul de țară pentru Croația este tratat corect ca "HR" (nu "CR").
- Operațiunile triunghiulare (cod T) **nu sunt automatizate** — clasificarea este integral manuală, făcută de contabil; aplicația nu generează niciodată automat acest tip.
- **Limitare cunoscută**: la data acestui ghid, aplicația nu are un flux de declarație rectificativă conform instrucțiunilor ANAF pentru D390 — antetul XML este generat mereu ca declarație inițială. Ceea ce apare în interfață drept "redepunere" este doar o evidență internă a depunerilor succesive, nu o rectificativă bifată conform normei. Corectarea unei perioade deja depuse trebuie tratată separat, în afara fluxului standard al aplicației.

[iConta.eu](/)
