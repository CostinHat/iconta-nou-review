---
title: "Livrare în lanț A-B-C cu un singur transport: cum stabilești locul fiecărei livrări la TVA?"
description: "Transportul se atribuie unei singure livrări din lanț; livrarea dinaintea ei are loc în statul de plecare, iar cea de după ea în statul de sosire. Contează cine organizează transportul."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Livrare în lanț A-B-C cu un singur transport: cum stabilești locul fiecărei livrări la TVA?

Într-un lanț A vinde lui B, B vinde lui C, iar marfa pleacă o singură dată, direct de la A la C. Există două livrări, dar un singur transport. La TVA, transportul se atribuie **unei singure livrări**. Doar aceea poate fi livrare intracomunitară scutită, iar locul ei este statul de plecare. Cealaltă e o livrare „fără transport": are loc acolo unde se află bunurile când sunt puse la dispoziția cumpărătorului. Dacă e înaintea transportului, asta înseamnă statul de plecare; dacă e după el, statul de sosire.

Cine primește transportul depinde de cine îl organizează.

## Temeiul legal

::: ghid-temei
„În cazul în care aceleași bunuri sunt livrate succesiv și sunt expediate sau transportate dintr-un stat membru în alt stat membru direct de la primul furnizor la ultimul client din lanț, expedierea sau transportul este atribuit numai livrării efectuate către operatorul intermediar."
— Codul fiscal (Legea 227/2015), art. 275 alin. (9) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Prin excepție de la dispozițiile alin. (9) [...] expedierea sau transportul este atribuit numai livrării de bunuri efectuate de către operatorul intermediar în cazul în care operatorul intermediar a comunicat furnizorului său codul său de înregistrare în scopuri de TVA care i-a fost eliberat de către statul membru din care sunt expediate sau transportate bunurile."
— Codul fiscal (Legea 227/2015), art. 275 alin. (10) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„În sensul prezentului articol, ”operator intermediar” înseamnă un furnizor din lanț, altul decât primul furnizor din lanț, care expediază sau transportă bunurile, fie el însuși, fie prin intermediul unei părți terțe care acționează în numele său."
— Codul fiscal (Legea 227/2015), art. 275 alin. (11) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

::: ghid-temei
„În al doilea caz, dacă persoana obligată să realizeze transportul este C, pe relația A-B se consideră o livrare fără transport, locul livrării fiind locul unde bunurile sunt puse la dispoziția lui B, iar în relația B-C se consideră o livrare cu transport, locul livrării fiind locul unde începe transportul, respectiv în statul membru al furnizorului A, unde se află bunurile atunci când începe transportul."
— Normele metodologice ale Codului fiscal (HG 1/2016), titlul VII, pct. 11 alin. (3) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

Cele patru situații:

| Cine transportă | Livrarea cu transport | A→B | B→C |
|---|---|---|---|
| A (primul furnizor) | A→B | în statul de plecare, poate fi scutită | în statul de sosire |
| B, regula de bază (alin. (9)) | A→B | în statul de plecare, poate fi scutită | în statul de sosire |
| B, cu codul de TVA din statul de plecare (alin. (10)) | B→C | în statul de plecare, taxabilă local | în statul de plecare, poate fi scutită |
| C (ultimul client) | B→C | în statul de plecare, taxabilă local | în statul de plecare, poate fi scutită |

Exemplul din norme e anterior regulilor din 2020 și nu tratează codul intermediarului din statul de plecare. Pentru B care transportă se aplică art. 275 alin. (9)-(11).

::: ghid-exemplu
SC Exemplu SRL (România, B) cumpără mărfuri de 30.000 euro de la un furnizor din Italia (A) și le vinde unui client din Germania (C). SC Exemplu SRL organizează transportul Italia–Germania și comunică furnizorului codul de TVA românesc. Transportul se atribuie livrării A→B, livrare intracomunitară scutită din Italia. Livrarea B→C are loc în Germania. Fiind trei state diferite, B poate aplica simplificarea pentru operațiuni triunghiulare, iar TVA-ul pentru livrarea către C îl datorează clientul german. În D390, SC Exemplu SRL raportează livrarea către C cu codul de operațiune triunghiulară (T).
:::

## Ce se greșește în practică

- Se tratează ambele livrări ca intracomunitare scutite. Doar una poate fi, cea căreia i se atribuie transportul.
- Operatorul intermediar comunică, fără să-și dea seama, codul de TVA din statul de plecare. Prin asta mută transportul pe livrarea lui (alin. (10)), iar factura primită de la A trebuie să fie cu TVA local.
- Se aplică regula intermediarului și când transportul îl face clientul final. C nu e „operator intermediar", pentru că nu e furnizor în lanț.
- Se uită că livrarea „fără transport" de după cea intracomunitară are loc în statul de sosire. Furnizorul ei poate avea obligații de TVA acolo, dacă nu se aplică simplificarea triunghiulară.

## Ce face iConta.eu

Modulul de operațiuni intracomunitare din iConta.eu gestionează livrările și achizițiile intracomunitare cu verificarea codului de TVA al partenerului în VIES și taxarea inversă 4426 = 4427, iar declarația D390 se generează din facturi. Maparea automată e: factură emisă → livrare (L), factură primită → achiziție (A). Operațiunile triunghiulare (T) se clasifică manual de contabil. Pentru ele, aplicația semnalează că maparea în D300 nu e încă acoperită automat, așa că decontul se verifică manual. Atribuirea transportului în lanț rămâne decizia contabilului.

[iConta.eu](/)
