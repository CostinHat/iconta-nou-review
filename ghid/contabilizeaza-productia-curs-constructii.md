---
title: "Cum se contabilizează producția în curs la construcții?"
description: "Regulile OMFP 1802/2014 pentru producția în curs sunt generale, pe sector, și se aplică și în construcții — fără o metodă alternativă de tip grad de execuție."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează producția în curs la construcții?

O firmă de construcții care nu finalizează o lucrare până la sfârșitul lunii are, la fel ca orice alt producător, un stoc de producție în curs de execuție. Mulți contabili din domeniu caută o metodă „specială" pentru construcții, de tip procent de finalizare (percentage-of-completion). Este util de știut, de la bun început: reglementarea contabilă românească nu prevede o metodă separată pentru construcții — se aplică regula generală.

## Temeiul legal

::: ghid-temei
„Contul 331 „Produse în curs de execuție" Cu ajutorul acestui cont se ține evidența stocurilor de produse în curs de execuție (care nu au trecut prin toate fazele de prelucrare prevăzute de procesul tehnologic, respectiv producția neterminată) existente la sfârșitul perioadei. [...] În debitul contului 331 [...] se înregistrează: – valoarea la cost de producție a stocului de produse în curs de execuție la sfârșitul perioadei, stabilită pe bază de inventar (711). [...] Soldul contului reprezintă valoarea la cost de producție a produselor aflate în curs de execuție la sfârșitul perioadei."
— OMFP 1802/2014, Reglementările contabile, Cap. 16, funcțiunea contului 331 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Aplicat la o lucrare de construcții nefinalizată la sfârșitul lunii:

- Lucrarea neterminată intră sub definiția generală de „producție neterminată, care nu a trecut prin toate fazele procesului tehnologic" — deci se contabilizează prin contul 331, exact ca la orice alt producător.
- Valoarea se stabilește **pe bază de inventar** (situație de lucrări, devize de execuție, stadii fizice) la cost de producție efectiv acumulat până la sfârșitul lunii — nu printr-o formulă separată de tip „grad de execuție" pe venituri.
- Mecanismul contabil rămâne cel standard, în doi timpi: constatare la sfârșit de lună (`331 = 711`) și reluare la începutul lunii următoare (`711 = 331`).

## Ce se greșește în practică

- Se caută sau se inventează o „metodă specială pentru construcții" (recunoaștere procentuală a veniturilor pe stadiu de execuție) care nu are un temei distinct în reglementările contabile românești pentru evidența producției în curs — regula rămâne cea generală, pe cost de producție prin inventar.
- Se omite constatarea producției în curs pentru șantierele nefinalizate la lună, mai ales când facturarea se face doar la recepția finală a lucrării.
- Se evaluează producția în curs la preț de vânzare estimat al lucrării, în loc de cost de producție efectiv acumulat.

## Ce face iConta.eu

Din ecranul **Operațiuni speciale → Imobilizări**, operațiunea „Producție (711/345)" pentru producția în curs generează notele standard `331 = 711` (constatare) și `711 = 331` (reluare), pe baza sumei introduse de contabil. Mecanismul este identic, indiferent de domeniul de activitate — aplicația nu are, și nici legea locală analizată nu cere, un tratament dedicat pentru construcții (de tip grad de execuție). O firmă de construcții folosește exact același flux ca orice alt producător; specificul sectorului (devize, situații de lucrări) rămâne un proces de evaluare din afara aplicației, ale cărui rezultate (suma constatată) se introduc manual în notă.

[iConta.eu](/)
