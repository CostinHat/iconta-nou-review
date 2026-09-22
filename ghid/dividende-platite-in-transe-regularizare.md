---
title: Dividende plătite în mai multe tranșe: cum se regularizează la final de an
description: O firmă care distribuie dividende trimestrial le înregistrează în contul 463, nu direct pe 457, iar la aprobarea situațiilor financiare anuale sumele plătite în avans se compensează cu dividendul anual aprobat, cu diferența de regularizat în 60 de zile.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se declară și se regularizează dividendele plătite în mai multe tranșe în cursul anului?

O firmă care nu vrea să aștepte până la închiderea exercițiului financiar poate distribui dividende trimestrial, pe baza situațiilor financiare interimare. Dar acele sume nu sunt dividende „finale" — ele rămân provizorii până la aprobarea situațiilor financiare anuale, când se face regularizarea. Diferența dintre contabilizarea corectă a acestui mecanism și tratarea distribuției trimestriale ca pe un dividend obișnuit ține de un singur cont: 463.

## Temeiul legal

::: ghid-temei
**Legea 31/1990, art. 67 alin. (1)-(2)** — mecanismul: „Cota-parte din profit ce se plătește fiecărui asociat constituie dividend." / „Dividendele se distribuie asociaților proporțional cu cota de participare la capitalul social vărsat, opțional trimestrial pe baza situațiilor financiare interimare și anual, după regularizarea efectuată prin situațiile financiare anuale, dacă prin actul constitutiv nu se prevede altfel. [...] regularizarea diferențelor rezultate din distribuirea dividendelor în timpul anului urmând să se facă prin situațiile financiare anuale. Plata diferențelor rezultate din regularizare se face în termen de 60 de zile de la data aprobării situațiilor financiare anuale [...]"

**Legea 31/1990, art. 67 alin. (2^2)** — dacă asociatul trebuie să restituie: „În cazul în care asociații sau acționarii datorează restituiri de dividende, în urma regularizării operate în situațiile financiare anuale, acestea se achită societății în termen de 60 de zile de la data aprobării situațiilor financiare anuale. În caz contrar, [...] datorează [...] dobândă penalizatoare [...]"

**OMFP 1802/2014, pct. 423^1** — contul folosit pentru distribuția trimestrială: „Entitățile care au optat, potrivit legii, să repartizeze dividende în cursul exercițiului financiar evidențiază acea repartizare în contul 463 «Creanțe reprezentând dividende repartizate în cursul exercițiului financiar» (articol contabil 463 «Creanțe [...]» = 456 «Decontări cu acționarii/asociații privind capitalul»)."

**OMFP 1802/2014, pct. 423^2** — regularizarea: „Dividendele repartizate conform pct. 423^1 se regularizează pe seama dividendelor distribuite pe baza situațiilor financiare anuale aprobate potrivit legii (articol contabil 457 «Dividende de plată» = 463 «Creanțe [...]»)."
:::

## Cum se înregistrează, pas cu pas

**La fiecare distribuție trimestrială** (nu direct pe 457, ci pe 463):

- `463 = 456` — cu dividendul brut repartizat trimestrial
- `456 = 446` — cu impozitul pe dividende (16% din brut, de la 1 ianuarie 2026)
- `456 = 5121` — cu dividendul net, la plata efectivă către asociat

**La aprobarea situațiilor financiare anuale**, se compară totalul plătit trimestrial cu dividendul anual aprobat de AGA:

- `1171 = 457` — dividendul anual aprobat
- `457 = 463` — cu suma cea mai mică dintre totalul plătit trimestrial și dividendul anual aprobat (compensarea interimarului cu anualul)

Dacă totalul plătit trimestrial a fost **mai mic** decât dividendul anual aprobat, diferența rămasă pe 457 se plătește asociatului ca dividend suplimentar, în cele 60 de zile de la aprobare.

Dacă totalul plătit trimestrial a fost **mai mare** decât dividendul anual aprobat, asociatul a încasat un exces și trebuie să îl restituie firmei tot în 60 de zile (art. 67 alin. (2^2)), cu dobândă penalizatoare dacă nu o face la termen. Acest exces rămas în sold pe 463 se stinge prin creditarea contului 463, cu contrapartidă în contul prin care se face încasarea (512 sau 531) — conform funcțiunii contului 463 din OMFP 1802, unde „sumele încasate reprezentând restituiri de dividende datorate, conform legii" apar explicit în creditul lui 463.

## Un exemplu

::: ghid-exemplu
O firmă distribuie trimestrial dividende interimare însumând **150.000 lei brut** în cursul anului. La aprobarea situațiilor financiare anuale, AGA aprobă un dividend anual de **140.000 lei**.

- Compensare: `457 = 463` cu **140.000 lei** (minimul dintre 150.000 și 140.000)
- Exces de restituit de asociat: 150.000 − 140.000 = **10.000 lei**, care trebuie încasat de firmă de la asociat în 60 de zile de la aprobare, prin stingerea soldului rămas în contul 463

Dacă asociatul nu restituie cei 10.000 lei în termen, firma poate pretinde dobândă penalizatoare, conform art. 67 alin. (2^2).
:::

## Ce se greșește în practică

- **Se înregistrează direct pe 457 la fiecare distribuție trimestrială.** Contul 457 e rezervat dividendului aprobat prin situațiile financiare anuale; distribuția din cursul anului trece prin 463, conform pct. 423^1 din OMFP 1802.
- **Se omite regularizarea de la final de an.** Chiar dacă toate trimestrele au fost plătite corect, tot trebuie făcută comparația cu dividendul anual aprobat — inclusiv atunci când coincid, pentru ca soldul contului 463 să ajungă la zero.
- **Se ignoră excesul de restituit.** Dacă totalul plătit trimestrial depășește dividendul anual aprobat, diferența nu „se pierde" — asociatul o datorează firmei, cu termen de 60 de zile și cu risc de dobândă penalizatoare dacă nu o achită la timp.

## Ce face iConta.eu

Pentru distribuțiile de dividende interimare, aplicația înregistrează automat linia `463 = 456` cu dividendul brut, apoi `456 = 446` cu impozitul și `456 = 5121` cu net-ul plătit. Cota de impozit pe dividende e citită dintr-un registru cu evoluția istorică a cotei (5% până în 2022, 8% în 2023-2024, 10% în 2025, 16% de la 1 ianuarie 2026), aplicată automat în funcție de data operațiunii.

La regularizarea anuală, aplicația calculează automat suma compensată (minimul dintre totalul interimar și dividendul anual aprobat) și înregistrează linia `457 = 463`. Tratamentul exact al excesului de restituit, în cazul în care totalul plătit trimestrial depășește dividendul anual aprobat, este în curs de verificare internă — recomandăm confirmarea manuală a soldului contului 463 la finalul regularizării, pentru firmele care au distribuit dividende interimare peste dividendul aprobat ulterior.

[iConta.eu](/)
