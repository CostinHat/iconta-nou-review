---
title: "Confuzia dintre lichiditate și solvabilitate"
description: "Precizare de temei: nici lichiditatea, nici solvabilitatea nu au o definiție legală proprie; sursa reală identificată e obligația de a raporta riscul de lichiditate în raportul administratorilor, din OMFP 1802/2014."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Confuzia dintre lichiditate și solvabilitate

Precizare de temei, înainte de conținut: „lichiditatea" și „solvabilitatea", ca indicatori financiari cu formule precise, **nu au o definiție dintr-un act normativ dedicat** — sunt concepte de analiză financiară, uzuale în practica economică și bancară, nu termeni legali definiți explicit undeva. Ce am găsit cu temei verificabil e obligația legală ca raportul administratorilor unei firme să conțină informații despre expunerea firmei la riscul de lichiditate — o mențiune care confirmă relevanța conceptului, fără să îl definească formal.

## Temeiul legal

::: ghid-temei
„491. - (1) În măsura în care este necesar pentru a înțelege dezvoltarea, performanța sau poziția entității, analiza cuprinde indicatori-cheie de performanță financiari și, atunci când este cazul, nefinanciari relevanți pentru activitățile specifice [...]
(2) Raportul administratorilor oferă, de asemenea, informații despre: [...]
e) în ceea ce privește utilizarea de către entitate a instrumentelor financiare, dacă sunt semnificative pentru evaluarea activelor sale, a datoriilor, a poziției financiare și a profitului sau pierderii: [...] expunerea entității la riscul de preț, riscul de credit, riscul de lichiditate și la riscul fluxului de numerar."
— OMFP 1802/2014 (Reglementările contabile privind situațiile financiare anuale individuale și consolidate), pct. 491 alin. (1), (2) lit. e) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Dat fiind că norma nu definește termenii, distincția de mai jos e prezentată ca **practică uzuală de analiză financiară**, nu ca definiție legală:

- **Lichiditatea** măsoară capacitatea unei firme de a-și onora obligațiile **pe termen scurt** (datorii curente, scadente în următoarele 12 luni), folosind activele circulante disponibile — numerar, creanțe, stocuri ușor transformabile în bani. O firmă e „lichidă" dacă poate plăti facturile și salariile din luna curentă.
- **Solvabilitatea** măsoară capacitatea unei firme de a-și onora **toate** obligațiile, pe termen lung, folosind totalul activelor — inclusiv cele imobilizate (clădiri, echipamente, participații). O firmă e „solvabilă" dacă, teoretic, și-ar putea achita toate datoriile prin valorificarea integrală a patrimoniului, chiar dacă asta ar dura ani.
- **Confuzia tipică**: o firmă poate fi solvabilă (activele depășesc cu mult datoriile totale) și, în același timp, nelichidă (nu are suficient numerar/active ușor transformabile pentru a plăti o factură scadentă săptămâna asta) — de exemplu, o firmă cu multe imobile și puțini bani în cont.
- **Riscul de lichiditate**, expres menționat de OMFP 1802/2014 pct. 491 alin. (2) lit. e), e riscul ca firma să nu poată onora obligațiile pe termen scurt din cauza lipsei de active ușor transformabile în numerar la momentul scadenței — exact zona unde apare confuzia cu solvabilitatea.

## Ce se greșește în practică

- Se raportează firma ca fiind „în siguranță financiară" doar pentru că activul net (solvabilitatea) e pozitiv, ignorând faptul că firma poate intra în incapacitate de plată pe termen scurt (problemă de lichiditate) chiar și cu un bilanț solid pe hârtie.
- Se confundă analiza de lichiditate cu simpla verificare a soldului din contul bancar la un moment dat, fără să se ia în calcul obligațiile scadente în perioada imediat următoare.
- Se presupune că o firmă profitabilă e automat lichidă — profitul contabil (rezultat din contul de profit și pierdere) nu echivalează cu disponibilul de numerar; o firmă poate fi profitabilă și, simultan, să nu aibă bani lichizi din cauza creanțelor neîncasate.

## Ce face iConta.eu

Aplicația generează situațiile financiare (bilanț, cont de profit și pierdere) din care se pot calcula manual indicatorii de lichiditate și solvabilitate, pe baza datelor contabile introduse. La data acestui ghid, iConta.eu **nu calculează automat acești indicatori** ca rapoarte dedicate — nu există în cod o funcție care să producă, de exemplu, „rata lichidității curente" sau „rata solvabilității generale"; contabilul îi calculează manual, din cifrele bilanțului, sau folosește instrumente separate de analiză financiară.

[iConta.eu](/)
