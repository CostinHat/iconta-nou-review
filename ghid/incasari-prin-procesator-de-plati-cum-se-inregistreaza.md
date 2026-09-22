---
title: Încasări prin procesator de plăți: cum se înregistrează?
description: Când un procesator de plăți virează suma netă (după reținerea comisionului propriu), în Registrul-jurnal trebuie înregistrată suma brută încasată de la client ca venit, iar comisionul reținut separat, ca o cheltuială deductibilă.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Încasări prin procesator de plăți: cum se înregistrează?

Multe PFA-uri încasează plăți prin procesatoare (PayPal, Stripe, marketplace-uri, platforme de curierat cu plată la livrare procesată central) care virează în cont suma netă, după ce își rețin propriul comision. Aici apare o greșeală frecventă și cu impact fiscal real: înregistrarea directă a sumei nete din extras ca venit total, fără să se reflecte separat venitul brut și comisionul.

## Temeiul legal

::: ghid-temei
Codul fiscal, art. 68 alin. (2) lit. a): venitul brut cuprinde "sumele încasate și echivalentul în lei al veniturilor în natură din desfășurarea activității".

HG 1/2016 (Norme metodologice), pct. 7 alin. (5) lit. f) și w): cheltuieli deductibile exemplificative — "f) cheltuielile cu comisioanele și cu alte servicii bancare; ... w) alte cheltuieli efectuate în scopul realizării veniturilor."

OMFP 170/2015, Cap. V, Secțiunea a 2-a: "În Registrul-jurnal de încasări şi plăți se înregistrează atât operațiunile în numerar, cât şi cele efectuate prin contul curent de la bancă, la valoarea prevăzută în documentele justificative, inclusiv taxa pe valoarea adăugată."
:::

## Principiul: brut la încasări, comisionul separat la plăți

Din combinația celor două texte rezultă un principiu clar: venitul brut este suma pe care o datorează clientul (sau pe care o generează vânzarea), nu suma care ajunge efectiv în cont după reținerea comisionului procesatorului. Comisionul reținut este, la rândul lui, o cheltuială deductibilă distinctă — dedusă separat, nu "compensată" tacit prin faptul că suma din extras e deja mai mică.

::: ghid-exemplu
Un client plătește 1.000 lei printr-un procesator care reține un comision de 3% (30 lei) și virează în contul PFA-ului doar 970 lei. Corect: se înregistrează o încasare de 1.000 lei (categoria "activitate", document justificativ factura/comanda) și o plată separată de 30 lei (categoria "cheltuiala_deductibila", document justificativ raportul procesatorului). Greșit: se înregistrează o singură încasare de 970 lei, ca și cum comisionul nici n-ar fi existat.
:::

Diferența nu e doar formală: dacă se înregistrează direct suma netă, cheltuiala cu comisionul dispare din evidență și din calculul deductibilităților, iar venitul brut raportat e subevaluat — ambele afectează, potențial, fișa de calcul D212.

## Ce se greșește în practică

- Se înregistrează în registru doar suma netă primită în cont, considerând-o "venitul din vânzare", fără să se mai treacă separat comisionul.
- Se preia automat suma din extrasul bancar ca venit unic, fără să se verifice dacă acea sumă e brută sau deja netă de comision.
- Nu se solicită/păstrează raportul de tranzacții al procesatorului, singurul document care arată clar suma brută și comisionul reținut.
- Se confundă comisionul reținut la sursă cu o reducere a prețului de vânzare, în loc să fie tratat ca o cheltuială separată.

## Ce face iConta.eu

`core/rip_api.py` nu impune el însuși disciplina brut/net: validarea (`_valideaza`) acceptă orice sumă pozitivă pe orice categorie validă, fără să verifice dacă suma introdusă corespunde valorii brute sau nete a tranzacției — decizia rămâne integral a contabilului la introducerea datelor. Funcția `import_banca` (liniile 140-160) preia direct suma din extrasul bancar ca ciornă la categoria `activitate`/venit, fără să știe dacă acea sumă e brută sau netă, pentru simplul motiv că extrasul bancar arată doar ce a intrat efectiv în cont. Practic, atunci când plata vine printr-un procesator care reține comision, contabilul trebuie să corecteze ciorna generată automat: să introducă suma brută ca încasare și să adauge separat o plată pentru comisionul reținut, pe baza raportului procesatorului.

[iConta.eu](/)
