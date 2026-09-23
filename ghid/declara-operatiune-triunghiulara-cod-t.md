---
title: "Cum se declară o operațiune triunghiulară cu cod T în D390?"
description: Codul T nu este niciodată dedus automat din facturi — se adaugă printr-o linie manuală, cu codul de TVA al beneficiarului final obligatoriu.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se declară o operațiune triunghiulară cu cod T în D390?

Codul **T** desemnează livrarea ulterioară de bunuri efectuată din România în cadrul unei operațiuni triunghiulare — situația în care firma ta este cumpărătorul revânzător dintr-un lanț cu trei persoane impozabile stabilite în trei state membre diferite. Este singurul cod din nomenclatorul D390 care nu are, în aplicație, nicio cale de derivare automată din facturi.

## Temeiul legal

::: ghid-temei
**OPANAF 705/2020, Anexa 2, Instrucțiuni pct. 1 lit. b)**:
> „[...] b) livrări ulterioare de bunuri efectuate în cadrul unei operaţiuni triunghiulare (T) [...]"

**Coloana „Cod operator intracomunitar" pentru T**:
> „în cazul livrărilor ulterioare de bunuri efectuate din România în cadrul unei operaţiuni triunghiulare (T) - codul de identificare în scopuri de TVA al persoanei beneficiare a livrării ulterioare, din al treilea stat membru, pe baza căruia cumpărătorul revânzător din România i-a efectuat livrarea ulterioară."
:::

Codul de operator este obligatoriu pentru T, la fel ca la L, P și R.

## Ce se greșește în practică

Greșeala frecventă este să se aștepte ca aplicația să recunoască „singură" o operațiune triunghiulară dintr-o factură emisă obișnuit — nu se întâmplă, iar factura rămâne implicit clasificată ca L (livrare simplă de bunuri) până la o intervenție explicită. A doua greșeală este completarea codului T cu codul de TVA al furnizorului inițial din lanț, în loc de codul beneficiarului final, singurul corect conform normei citate mai sus.

## Ce face iConta.eu

Codul T nu este produs niciodată automat de motorul de clasificare, indiferent de conținutul facturilor din perioadă — trebuie introdus explicit din panoul de clasificare D390 (pasul 2 al declarației), în una din cele două forme: reclasificarea unei operațiuni auto-derivate din L în T (dacă factura corespunzătoare nu a fost creată prin ecranul dedicat de livrare intracomunitară — vezi limitarea de mai jos), sau adăugarea unei linii pur manuale de tip T, cu țara și codul beneficiarului final completate obligatoriu.

**De reconfirmat pe comportamentul live**: pentru o factură emisă prin ecranul dedicat „Livrare intracomunitară" (nu prin emiterea obișnuită), aplicația reține la creare axa bunuri/servicii a documentului, iar conform codului verificat, aceasta pare să determine definitiv tipul D390 al operațiunii — reclasificarea ulterioară din panou, inclusiv către T, ar putea să nu aibă efect vizibil în declarația generată pentru acest caz, fără un avertisment explicit în interfață. Dacă operațiunea triunghiulară provine dintr-o astfel de factură, recomandăm verificarea directă a XML-ului generat după reclasificare, sau folosirea liniei pur manuale de tip T ca alternativă mai sigură.

[iConta.eu](/)
