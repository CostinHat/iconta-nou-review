---
title: "Cum tratez fiscal cheltuielile de protocol în 2026?"
description: "Regula de bază pentru cheltuielile de protocol rămâne neschimbată în 2026: deductibilitate limitată la 2% dintr-o bază calculată pe profitul contabil, cu reguli speciale pentru cadourile peste 100 lei."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum tratez fiscal cheltuielile de protocol în 2026?

„Protocol" înseamnă, fiscal, mesele de afaceri, cadourile oferite partenerilor și alte cheltuieli similare făcute pentru a întreține relații de afaceri — categorie distinctă de reclamă și publicitate, care sunt deductibile integral. Pentru 2026, regula de calcul a plafonului de deductibilitate a rămas cea din Codul fiscal, fără o modificare specifică identificată pentru acest tip de cheltuială.

## Temeiul legal

::: ghid-temei
„Următoarele cheltuieli au deductibilitate limitată: a) cheltuielile de protocol în limita unei cote de 2% aplicată asupra profitului contabil la care se adaugă cheltuielile cu impozitul pe profit și cheltuielile de protocol. În cadrul cheltuielilor de protocol se includ și cheltuielile înregistrate cu taxa pe valoarea adăugată colectată potrivit prevederilor titlului VII, pentru cadourile oferite de contribuabil, cu valoare mai mare de 100 lei."
— Legea nr. 227/2015 (Codul fiscal), art. 25 alin. (3) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Sunt cheltuieli de protocol cele făcute pentru **reprezentare** (mese, cadouri, evenimente cu parteneri de afaceri) — nu se confundă cu reclama/publicitatea, care e deductibilă integral, dacă e făcută în scopul activității.
- Pentru **cadourile cu valoare mai mare de 100 lei**, TVA colectată aferentă (tratată ca livrare către sine, potrivit titlului VII din Codul fiscal) se include în valoarea cheltuielii de protocol supuse plafonului de 2%.
- Justificarea documentară contează la fel de mult ca încadrarea în plafon: fără document care să arate scopul de afaceri al cheltuielii (factură, listă de participanți, justificare a evenimentului), riscul e ca suma să fie considerată nedeductibilă integral, nu doar peste plafon.
- Nu am identificat, la verificarea în `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, o modificare a cotei de 2% sau a bazei de calcul aplicabilă specific anului 2026 — regula rămâne cea din art. 25 alin. (3) lit. a).

## Ce se greșește în practică

- Se încadrează la protocol cheltuieli care sunt, de fapt, reclamă/publicitate (materiale promoționale distribuite public, nu cadouri individuale către parteneri) și li se aplică plafonul de 2% fără să fie cazul.
- Se lasă cheltuiala de protocol fără documentul justificativ care să arate scopul de afaceri, expunând întreaga sumă (nu doar partea peste plafon) unui risc de reîncadrare ca nedeductibilă la un control.
- Se omite TVA colectată pentru cadourile peste 100 lei din baza supusă plafonului de 2%, calculând un plafon mai mic decât cel real.

## Ce face iConta.eu

La data acestui ghid, iConta.eu permite înregistrarea cheltuielilor de protocol pe contul 623 (`core/plan_omfp.py`) și emiterea facturilor/documentelor aferente prin modulele de facturare existente. Aplicația nu are, la acest moment, un asistent care să distingă automat între cheltuieli de protocol și de reclamă pe baza descrierii sau să calculeze TVA colectată pentru cadourile peste 100 lei ca livrare către sine — încadrarea corectă a fiecărei cheltuieli rămâne o decizie a contabilului.

[iConta.eu](/)
